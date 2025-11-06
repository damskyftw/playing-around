"""
Browser-based crawler using Playwright to bypass bot protection
"""
from playwright.sync_api import sync_playwright, Page, Browser
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from typing import Set, List
import time


class BrowserCrawler:
    """Crawls documentation sites using a headless browser"""

    def __init__(self, base_url: str, max_pages: int = 500, delay: float = 1.0):
        """
        Initialize the browser crawler

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

    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and trailing slashes"""
        parsed = urlparse(url)
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

    def extract_links(self, html: str, current_url: str) -> List[str]:
        """Extract all valid links from HTML"""
        soup = BeautifulSoup(html, 'lxml')
        links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            absolute_url = urljoin(current_url, href)
            normalized = self.normalize_url(absolute_url)

            if self.is_valid_url(normalized):
                links.append(normalized)

        return links

    def crawl(self) -> List[str]:
        """
        Crawl the documentation site using a headless browser

        Returns:
            List of all discovered URLs
        """
        print(f"Starting browser-based crawl of {self.base_url}")

        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()

            try:
                while self.to_visit and len(self.visited_urls) < self.max_pages:
                    current_url = self.to_visit.pop(0)

                    # Skip if already visited
                    if current_url in self.visited_urls:
                        continue

                    try:
                        print(f"Crawling [{len(self.visited_urls) + 1}/{self.max_pages}]: {current_url}")

                        # Navigate to page
                        response = page.goto(current_url, wait_until='networkidle', timeout=30000)

                        if not response or response.status != 200:
                            print(f"Failed to load {current_url}: status {response.status if response else 'None'}")
                            continue

                        # Wait a bit for any dynamic content
                        page.wait_for_timeout(2000)

                        # Mark as visited
                        self.visited_urls.add(current_url)

                        # Get page content
                        html = page.content()

                        # Extract links
                        links = self.extract_links(html, current_url)

                        # Add new links to queue
                        for link in links:
                            if link not in self.visited_urls and link not in self.to_visit:
                                self.to_visit.append(link)

                        # Be respectful with delays
                        time.sleep(self.delay)

                    except Exception as e:
                        print(f"Error crawling {current_url}: {e}")
                        continue

            finally:
                browser.close()

        print(f"Crawl complete! Found {len(self.visited_urls)} pages")
        return list(self.visited_urls)


def get_page_content(url: str) -> str:
    """
    Get content of a single page using Playwright

    Args:
        url: URL to fetch

    Returns:
        HTML content of the page
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            html = page.content()
            return html
        finally:
            browser.close()
