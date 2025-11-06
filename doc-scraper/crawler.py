"""
URL Crawler for discovering documentation pages
"""
import requests
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from typing import Set, List, Optional
import time
import xml.etree.ElementTree as ET


class DocumentationCrawler:
    """Crawls documentation sites to discover all pages"""

    def __init__(self, base_url: str, max_pages: int = 500, delay: float = 0.5):
        """
        Initialize the crawler

        Args:
            base_url: The base URL of the documentation site
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.to_visit: List[str] = [base_url]

        # Parse base domain to stay within it
        parsed = urlparse(base_url)
        self.base_domain = parsed.netloc
        self.base_scheme = parsed.scheme

        # Headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and trailing slashes"""
        parsed = urlparse(url)
        # Remove fragment and query for normalization
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path.rstrip('/'),
            '',
            '',
            ''
        ))
        return normalized

    def is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled"""
        parsed = urlparse(url)

        # Must be same domain
        if parsed.netloc != self.base_domain:
            return False

        # Skip common non-documentation paths
        skip_paths = [
            '/search', '/login', '/logout', '/api/',
            '.pdf', '.zip', '.tar.gz', '.jpg', '.png', '.gif',
            '.css', '.js', '.ico', '/edit/', '/delete/'
        ]

        path_lower = parsed.path.lower()
        for skip in skip_paths:
            if skip in path_lower:
                return False

        return True

    def try_sitemap(self) -> List[str]:
        """Try to get URLs from sitemap.xml"""
        sitemap_urls = [
            f"{self.base_url}/sitemap.xml",
            f"{self.base_url}/sitemap_index.xml",
        ]

        urls = []
        for sitemap_url in sitemap_urls:
            try:
                response = requests.get(sitemap_url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    # Handle namespace
                    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

                    # Try to find URLs
                    for loc in root.findall('.//ns:loc', ns):
                        if loc.text:
                            urls.append(loc.text)

                    # Also try without namespace (some sitemaps don't use it)
                    if not urls:
                        for loc in root.findall('.//loc'):
                            if loc.text:
                                urls.append(loc.text)

                    if urls:
                        print(f"Found {len(urls)} URLs in sitemap")
                        return urls
            except Exception as e:
                print(f"Could not fetch sitemap from {sitemap_url}: {e}")
                continue

        return []

    def extract_links(self, html: str, current_url: str) -> List[str]:
        """Extract all valid links from HTML"""
        soup = BeautifulSoup(html, 'lxml')
        links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Make absolute URL
            absolute_url = urljoin(current_url, href)

            # Normalize and validate
            normalized = self.normalize_url(absolute_url)

            if self.is_valid_url(normalized):
                links.append(normalized)

        return links

    def crawl(self) -> List[str]:
        """
        Crawl the documentation site and return all discovered URLs

        Returns:
            List of all discovered URLs
        """
        print(f"Starting crawl of {self.base_url}")

        # Try sitemap first
        sitemap_urls = self.try_sitemap()
        if sitemap_urls:
            # Filter and normalize sitemap URLs
            valid_urls = [
                self.normalize_url(url)
                for url in sitemap_urls
                if self.is_valid_url(url)
            ]
            return valid_urls[:self.max_pages]

        print("No sitemap found, crawling manually...")

        # Manual crawl
        while self.to_visit and len(self.visited_urls) < self.max_pages:
            current_url = self.to_visit.pop(0)

            # Skip if already visited
            if current_url in self.visited_urls:
                continue

            try:
                print(f"Crawling [{len(self.visited_urls) + 1}/{self.max_pages}]: {current_url}")

                # Fetch the page
                response = requests.get(current_url, headers=self.headers, timeout=10)
                response.raise_for_status()

                # Mark as visited
                self.visited_urls.add(current_url)

                # Extract links
                links = self.extract_links(response.text, current_url)

                # Add new links to queue
                for link in links:
                    if link not in self.visited_urls and link not in self.to_visit:
                        self.to_visit.append(link)

                # Be respectful with delays
                time.sleep(self.delay)

            except Exception as e:
                print(f"Error crawling {current_url}: {e}")
                continue

        print(f"Crawl complete! Found {len(self.visited_urls)} pages")
        return list(self.visited_urls)
