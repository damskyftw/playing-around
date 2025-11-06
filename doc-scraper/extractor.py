"""
Content extractor for cleaning HTML and converting to markdown
"""
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from typing import Dict, Optional
import re


class ContentExtractor:
    """Extracts clean content from documentation HTML"""

    def __init__(self):
        """Initialize the content extractor"""
        # Common selectors for main content in documentation sites
        self.content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.main-content',
            '.content',
            '.documentation',
            '.doc-content',
            '#content',
            '#main-content',
            '.markdown-body',
            '.rst-content',
        ]

        # Selectors to remove (navigation, footer, etc.)
        self.remove_selectors = [
            'nav',
            'header',
            'footer',
            '.navigation',
            '.sidebar',
            '.toc',
            '.table-of-contents',
            '.breadcrumb',
            '.edit-page',
            '.next-page',
            '.prev-page',
            '.search',
            'script',
            'style',
            '.advertisement',
            '.ad',
        ]

    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        # Fall back to title tag
        title = soup.find('title')
        if title:
            return title.get_text().strip()

        return "Untitled"

    def extract_main_content(self, html: str) -> BeautifulSoup:
        """Extract the main content area from HTML"""
        soup = BeautifulSoup(html, 'lxml')

        # Try to find main content area
        main_content = None
        for selector in self.content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')

        # If still nothing, use entire soup
        if not main_content:
            main_content = soup

        return main_content

    def clean_content(self, content: BeautifulSoup) -> BeautifulSoup:
        """Remove unwanted elements from content"""
        # Remove unwanted elements
        for selector in self.remove_selectors:
            for element in content.select(selector):
                element.decompose()

        # Remove comments
        for comment in content.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            comment.extract()

        return content

    def html_to_markdown(self, html_content: BeautifulSoup) -> str:
        """Convert HTML to clean markdown"""
        # Convert to markdown
        markdown = md(
            str(html_content),
            heading_style="ATX",
            bullets="-",
            code_language="",
            strip=['script', 'style']
        )

        # Clean up the markdown
        # Remove excessive blank lines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        # Remove leading/trailing whitespace
        markdown = markdown.strip()

        return markdown

    def extract(self, html: str, url: str) -> Dict[str, str]:
        """
        Extract clean content from HTML page

        Args:
            html: Raw HTML content
            url: URL of the page (for reference)

        Returns:
            Dictionary with title, markdown content, and URL
        """
        soup = BeautifulSoup(html, 'lxml')

        # Extract title
        title = self.extract_title(soup)

        # Extract main content
        main_content = self.extract_main_content(html)

        # Clean content
        cleaned_content = self.clean_content(main_content)

        # Convert to markdown
        markdown = self.html_to_markdown(cleaned_content)

        return {
            'title': title,
            'content': markdown,
            'url': url
        }
