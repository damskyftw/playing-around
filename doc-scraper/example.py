#!/usr/bin/env python3
"""
Example usage of the Documentation Scraper
"""
from scraper import DocumentationScraper


def example_basic_scraping():
    """Basic scraping example"""
    print("="*60)
    print("Example 1: Basic Scraping")
    print("="*60)

    # Initialize scraper
    scraper = DocumentationScraper(
        storage_dir="./example_docs",
        max_pages=50,  # Limit for demo
        delay=0.5
    )

    # Scrape a documentation site
    # Using a smaller docs site for demo
    result = scraper.scrape("https://www.example.com")

    if result['success']:
        print(f"\n✓ Successfully scraped {result['total_pages']} pages")
        print(f"✓ Stored in: {result['storage_dir']}")
    else:
        print(f"\n✗ Failed: {result.get('error', 'Unknown error')}")


def example_search():
    """Search example"""
    print("\n" + "="*60)
    print("Example 2: Searching Documentation")
    print("="*60)

    scraper = DocumentationScraper(storage_dir="./example_docs")

    # Search for content
    results = scraper.search("www.example.com", "example")

    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results[:5], 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Context: {result['context']}")


def example_list_and_info():
    """List sites and get info example"""
    print("\n" + "="*60)
    print("Example 3: Listing Sites and Getting Info")
    print("="*60)

    scraper = DocumentationScraper(storage_dir="./example_docs")

    # List all scraped sites
    sites = scraper.list_sites()
    print(f"\nScraped sites ({len(sites)}):")
    for site in sites:
        print(f"  - {site}")

    # Get info about a specific site
    if sites:
        site_name = sites[0]
        info = scraper.get_site_info(site_name)

        if info:
            print(f"\nSite: {info['site_name']}")
            print(f"Total pages: {info['total_pages']}")
            print("\nFirst 5 pages:")
            for page in info['pages'][:5]:
                print(f"  - {page['title']}")


def example_read_page():
    """Read a specific page example"""
    print("\n" + "="*60)
    print("Example 4: Reading a Specific Page")
    print("="*60)

    scraper = DocumentationScraper(storage_dir="./example_docs")

    # Get site info
    sites = scraper.list_sites()
    if not sites:
        print("No sites available. Run scraping first.")
        return

    site_name = sites[0]
    info = scraper.get_site_info(site_name)

    if info and info['pages']:
        # Read the first page
        first_page = info['pages'][0]
        content = scraper.get_page(site_name, first_page['filename'])

        print(f"\nReading: {first_page['title']}")
        print("-" * 60)
        print(content[:500])  # Show first 500 chars
        print("...")


if __name__ == "__main__":
    print("\nDocumentation Scraper - Example Usage\n")

    # Run examples
    # NOTE: Modify the URL in example_basic_scraping() to test with real docs

    # Uncomment the examples you want to run:
    # example_basic_scraping()
    # example_search()
    # example_list_and_info()
    # example_read_page()

    print("\n" + "="*60)
    print("To run examples, uncomment the function calls in example.py")
    print("="*60)
