"""
Storage system for documentation
"""
import os
import json
import hashlib
from typing import Dict, List, Optional
from pathlib import Path
from urllib.parse import urlparse


class DocumentationStorage:
    """Handles storage and retrieval of scraped documentation"""

    def __init__(self, base_dir: str = "./scraped_docs"):
        """
        Initialize storage

        Args:
            base_dir: Base directory for storing documentation
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_doc_dir(self, site_name: str) -> Path:
        """Get directory for a specific documentation site"""
        # Clean site name for filesystem
        clean_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in site_name)
        doc_dir = self.base_dir / clean_name
        doc_dir.mkdir(parents=True, exist_ok=True)
        return doc_dir

    def url_to_filename(self, url: str) -> str:
        """Convert URL to a safe filename"""
        # Parse URL
        parsed = urlparse(url)

        # Use path as base
        path = parsed.path.strip('/')

        # If empty, use 'index'
        if not path:
            path = 'index'

        # Replace slashes with underscores
        filename = path.replace('/', '_')

        # Clean up
        filename = "".join(c if c.isalnum() or c in ['-', '_', '.'] else '_' for c in filename)

        # Add hash of full URL to ensure uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"{filename}_{url_hash}"

        return f"{filename}.md"

    def save_page(self, site_name: str, page_data: Dict[str, str]) -> str:
        """
        Save a documentation page

        Args:
            site_name: Name of the documentation site
            page_data: Dictionary with 'title', 'content', and 'url'

        Returns:
            Path to saved file
        """
        doc_dir = self.get_doc_dir(site_name)

        # Create filename from URL
        filename = self.url_to_filename(page_data['url'])
        filepath = doc_dir / filename

        # Create markdown content with metadata
        markdown_content = f"""---
title: {page_data['title']}
url: {page_data['url']}
---

# {page_data['title']}

{page_data['content']}
"""

        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return str(filepath)

    def save_index(self, site_name: str, pages: List[Dict[str, str]]) -> str:
        """
        Save an index file with all pages

        Args:
            site_name: Name of the documentation site
            pages: List of page dictionaries with 'title', 'url', and 'filename'

        Returns:
            Path to index file
        """
        doc_dir = self.get_doc_dir(site_name)
        index_path = doc_dir / "index.json"

        index_data = {
            'site_name': site_name,
            'total_pages': len(pages),
            'pages': pages
        }

        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)

        return str(index_path)

    def load_index(self, site_name: str) -> Optional[Dict]:
        """Load index for a documentation site"""
        doc_dir = self.get_doc_dir(site_name)
        index_path = doc_dir / "index.json"

        if not index_path.exists():
            return None

        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_sites(self) -> List[str]:
        """List all scraped documentation sites"""
        if not self.base_dir.exists():
            return []

        sites = []
        for item in self.base_dir.iterdir():
            if item.is_dir():
                sites.append(item.name)

        return sites

    def get_page_content(self, site_name: str, filename: str) -> Optional[str]:
        """Get content of a specific page"""
        doc_dir = self.get_doc_dir(site_name)
        filepath = doc_dir / filename

        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def search_content(self, site_name: str, query: str) -> List[Dict[str, str]]:
        """
        Search for query in documentation content

        Args:
            site_name: Name of the documentation site
            query: Search query

        Returns:
            List of matching pages with context
        """
        doc_dir = self.get_doc_dir(site_name)
        query_lower = query.lower()
        results = []

        # Load index to get page info
        index = self.load_index(site_name)
        if not index:
            return results

        # Search through each page
        for page in index['pages']:
            filepath = doc_dir / page['filename']

            if not filepath.exists():
                continue

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple search (case-insensitive)
            if query_lower in content.lower():
                # Find context around match
                content_lower = content.lower()
                idx = content_lower.find(query_lower)

                # Get surrounding context
                start = max(0, idx - 100)
                end = min(len(content), idx + 100)
                context = content[start:end]

                results.append({
                    'title': page['title'],
                    'url': page['url'],
                    'filename': page['filename'],
                    'context': f"...{context}..."
                })

        return results
