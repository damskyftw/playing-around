#!/usr/bin/env python3
"""
CLI interface for documentation scraper
"""
import argparse
import sys
from scraper import DocumentationScraper
from pathlib import Path


def cmd_scrape(args):
    """Scrape a documentation site"""
    scraper = DocumentationScraper(
        storage_dir=args.storage_dir,
        max_pages=args.max_pages,
        delay=args.delay,
        use_browser=args.browser
    )

    result = scraper.scrape(args.url, site_name=args.name)

    if result['success']:
        print("\n✓ Documentation successfully scraped!")
        return 0
    else:
        print(f"\n❌ Scraping failed: {result.get('error', 'Unknown error')}")
        return 1


def cmd_list(args):
    """List all scraped documentation sites"""
    scraper = DocumentationScraper(storage_dir=args.storage_dir)
    sites = scraper.list_sites()

    if not sites:
        print("No documentation sites scraped yet.")
        return 0

    print(f"\nScraped documentation sites ({len(sites)}):")
    print("-" * 60)

    for site in sites:
        info = scraper.get_site_info(site)
        if info:
            print(f"\n📚 {site}")
            print(f"   Pages: {info['total_pages']}")
            print(f"   Location: {scraper.storage.get_doc_dir(site)}")
        else:
            print(f"\n📚 {site}")

    print()
    return 0


def cmd_info(args):
    """Show information about a scraped site"""
    scraper = DocumentationScraper(storage_dir=args.storage_dir)
    info = scraper.get_site_info(args.site)

    if not info:
        print(f"❌ Site '{args.site}' not found")
        return 1

    print(f"\n📚 {info['site_name']}")
    print("=" * 60)
    print(f"Total pages: {info['total_pages']}")
    print(f"Location: {scraper.storage.get_doc_dir(args.site)}")
    print("\nPages:")
    print("-" * 60)

    for i, page in enumerate(info['pages'][:args.limit], 1):
        print(f"{i}. {page['title']}")
        print(f"   URL: {page['url']}")
        print(f"   File: {page['filename']}")
        print()

    if len(info['pages']) > args.limit:
        print(f"... and {len(info['pages']) - args.limit} more pages")

    return 0


def cmd_search(args):
    """Search documentation content"""
    scraper = DocumentationScraper(storage_dir=args.storage_dir)
    results = scraper.search(args.site, args.query)

    if not results:
        print(f"No results found for '{args.query}'")
        return 0

    print(f"\nFound {len(results)} results for '{args.query}':")
    print("=" * 60)

    for i, result in enumerate(results[:args.limit], 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Context: {result['context']}")
        print()

    if len(results) > args.limit:
        print(f"... and {len(results) - args.limit} more results")

    return 0


def cmd_read(args):
    """Read a specific page"""
    scraper = DocumentationScraper(storage_dir=args.storage_dir)

    # First, get the site info to find the page
    info = scraper.get_site_info(args.site)
    if not info:
        print(f"❌ Site '{args.site}' not found")
        return 1

    # Find page by title or filename
    page = None
    for p in info['pages']:
        if args.page.lower() in p['title'].lower() or args.page in p['filename']:
            page = p
            break

    if not page:
        print(f"❌ Page '{args.page}' not found in site '{args.site}'")
        print("\nAvailable pages:")
        for p in info['pages'][:10]:
            print(f"  - {p['title']}")
        if len(info['pages']) > 10:
            print(f"  ... and {len(info['pages']) - 10} more")
        return 1

    # Read the page content
    content = scraper.get_page(args.site, page['filename'])
    if not content:
        print(f"❌ Could not read page content")
        return 1

    print(content)
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Documentation Scraper - Scrape and store documentation sites",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Global arguments
    parser.add_argument(
        '--storage-dir',
        default='./scraped_docs',
        help='Directory to store scraped documentation (default: ./scraped_docs)'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape a documentation site')
    scrape_parser.add_argument('url', help='Base URL of the documentation site')
    scrape_parser.add_argument('--name', help='Custom name for the site')
    scrape_parser.add_argument('--max-pages', type=int, default=500, help='Maximum pages to scrape (default: 500)')
    scrape_parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests in seconds (default: 0.5)')
    scrape_parser.add_argument('--browser', action='store_true', help='Use headless browser for bot-protected sites')
    scrape_parser.set_defaults(func=cmd_scrape)

    # List command
    list_parser = subparsers.add_parser('list', help='List all scraped documentation sites')
    list_parser.set_defaults(func=cmd_list)

    # Info command
    info_parser = subparsers.add_parser('info', help='Show information about a scraped site')
    info_parser.add_argument('site', help='Name of the site')
    info_parser.add_argument('--limit', type=int, default=10, help='Number of pages to show (default: 10)')
    info_parser.set_defaults(func=cmd_info)

    # Search command
    search_parser = subparsers.add_parser('search', help='Search documentation content')
    search_parser.add_argument('site', help='Name of the site to search')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Number of results to show (default: 10)')
    search_parser.set_defaults(func=cmd_search)

    # Read command
    read_parser = subparsers.add_parser('read', help='Read a specific page')
    read_parser.add_argument('site', help='Name of the site')
    read_parser.add_argument('page', help='Page title or filename')
    read_parser.set_defaults(func=cmd_read)

    # Parse arguments
    args = parser.parse_args()

    # Show help if no command specified
    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
