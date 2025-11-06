"""
Main documentation scraper orchestrator
"""
import requests
from typing import List, Dict, Optional
from tqdm import tqdm
from urllib.parse import urlparse

from crawler import DocumentationCrawler
from extractor import ContentExtractor
from storage import DocumentationStorage


class DocumentationScraper:
    """Main scraper that coordinates crawling, extraction, and storage"""

    def __init__(
        self,
        storage_dir: str = "./scraped_docs",
        max_pages: int = 500,
        delay: float = 0.5
    ):
        """
        Initialize the scraper

        Args:
            storage_dir: Directory to store scraped documentation
            max_pages: Maximum number of pages to scrape
            delay: Delay between requests in seconds
        """
        self.storage = DocumentationStorage(storage_dir)
        self.extractor = ContentExtractor()
        self.max_pages = max_pages
        self.delay = delay

    def get_site_name(self, url: str) -> str:
        """Extract a clean site name from URL"""
        parsed = urlparse(url)
        # Use domain as site name
        domain = parsed.netloc.replace('www.', '')
        return domain

    def scrape(self, url: str, site_name: Optional[str] = None) -> Dict[str, any]:
        """
        Scrape a documentation site

        Args:
            url: Base URL of the documentation
            site_name: Optional custom name for the site

        Returns:
            Dictionary with scraping results
        """
        print(f"\n{'='*60}")
        print(f"Starting documentation scrape")
        print(f"URL: {url}")
        print(f"{'='*60}\n")

        # Determine site name
        if not site_name:
            site_name = self.get_site_name(url)

        print(f"Site name: {site_name}")

        # Step 1: Crawl to discover all URLs
        print("\n[Step 1/3] Crawling to discover pages...")
        crawler = DocumentationCrawler(url, max_pages=self.max_pages, delay=self.delay)
        urls = crawler.crawl()

        if not urls:
            print("❌ No URLs found!")
            return {
                'success': False,
                'error': 'No URLs discovered'
            }

        print(f"✓ Discovered {len(urls)} pages")

        # Step 2: Extract content from each page
        print(f"\n[Step 2/3] Extracting content from pages...")
        pages_data = []
        failed_urls = []

        for url in tqdm(urls, desc="Extracting"):
            try:
                # Fetch page
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                # Extract content
                page_data = self.extractor.extract(response.text, url)

                # Save page
                filename = self.storage.url_to_filename(url)
                filepath = self.storage.save_page(site_name, page_data)

                pages_data.append({
                    'title': page_data['title'],
                    'url': url,
                    'filename': filename,
                    'filepath': filepath
                })

            except Exception as e:
                failed_urls.append({'url': url, 'error': str(e)})
                continue

        print(f"✓ Extracted {len(pages_data)} pages")
        if failed_urls:
            print(f"⚠ Failed to extract {len(failed_urls)} pages")

        # Step 3: Save index
        print(f"\n[Step 3/3] Saving index...")
        index_path = self.storage.save_index(site_name, pages_data)
        print(f"✓ Index saved to: {index_path}")

        # Summary
        print(f"\n{'='*60}")
        print(f"Scraping Complete!")
        print(f"{'='*60}")
        print(f"Site: {site_name}")
        print(f"Total pages: {len(pages_data)}")
        print(f"Failed pages: {len(failed_urls)}")
        print(f"Storage location: {self.storage.get_doc_dir(site_name)}")
        print(f"{'='*60}\n")

        return {
            'success': True,
            'site_name': site_name,
            'total_pages': len(pages_data),
            'failed_pages': len(failed_urls),
            'pages': pages_data,
            'failed_urls': failed_urls,
            'storage_dir': str(self.storage.get_doc_dir(site_name)),
            'index_path': index_path
        }

    def list_sites(self) -> List[str]:
        """List all scraped documentation sites"""
        return self.storage.list_sites()

    def get_site_info(self, site_name: str) -> Optional[Dict]:
        """Get information about a scraped site"""
        return self.storage.load_index(site_name)

    def search(self, site_name: str, query: str) -> List[Dict[str, str]]:
        """Search documentation content"""
        return self.storage.search_content(site_name, query)

    def get_page(self, site_name: str, filename: str) -> Optional[str]:
        """Get content of a specific page"""
        return self.storage.get_page_content(site_name, filename)
