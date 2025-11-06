# Documentation Scraper

A powerful Python tool for scraping, storing, and searching documentation websites. Automatically crawls documentation sites, extracts clean content, converts to Markdown, and provides easy search and retrieval.

## Features

- **Automatic Crawling**: Discovers all pages via sitemap or recursive crawling
- **Smart Content Extraction**: Removes navigation, footers, ads, etc.
- **Markdown Conversion**: Stores content as clean, readable Markdown
- **Full-Text Search**: Search across all scraped documentation
- **CLI Interface**: Easy-to-use command-line interface
- **Python API**: Use programmatically in your own scripts
- **Rate Limiting**: Respectful crawling with configurable delays

## Installation

1. Install dependencies:

```bash
cd doc-scraper
pip install -r requirements.txt
```

2. Make CLI executable (optional):

```bash
chmod +x cli.py
```

## Quick Start

### Scrape a Documentation Site

```bash
python cli.py scrape https://docs.python.org/3/
```

With custom options:

```bash
python cli.py scrape https://docs.example.com \
  --name my-docs \
  --max-pages 200 \
  --delay 1.0 \
  --storage-dir ./my_docs
```

### List Scraped Sites

```bash
python cli.py list
```

### View Site Information

```bash
python cli.py info docs.python.org
```

Show more pages:

```bash
python cli.py info docs.python.org --limit 50
```

### Search Documentation

```bash
python cli.py search docs.python.org "async await"
```

### Read a Specific Page

```bash
python cli.py read docs.python.org "getting started"
```

## CLI Commands

### `scrape`

Scrape a documentation website.

```bash
python cli.py scrape <url> [options]
```

**Options:**
- `--name`: Custom name for the site (default: extracted from URL)
- `--max-pages`: Maximum pages to scrape (default: 500)
- `--delay`: Delay between requests in seconds (default: 0.5)
- `--storage-dir`: Storage directory (default: ./scraped_docs)

**Example:**
```bash
python cli.py scrape https://fastapi.tiangolo.com/ --max-pages 100
```

### `list`

List all scraped documentation sites.

```bash
python cli.py list [options]
```

**Options:**
- `--storage-dir`: Storage directory (default: ./scraped_docs)

### `info`

Show detailed information about a scraped site.

```bash
python cli.py info <site-name> [options]
```

**Options:**
- `--limit`: Number of pages to display (default: 10)
- `--storage-dir`: Storage directory (default: ./scraped_docs)

**Example:**
```bash
python cli.py info fastapi.tiangolo.com --limit 20
```

### `search`

Search documentation content.

```bash
python cli.py search <site-name> <query> [options]
```

**Options:**
- `--limit`: Number of results to show (default: 10)
- `--storage-dir`: Storage directory (default: ./scraped_docs)

**Example:**
```bash
python cli.py search fastapi.tiangolo.com "dependency injection"
```

### `read`

Read a specific documentation page.

```bash
python cli.py read <site-name> <page-title-or-filename>
```

**Example:**
```bash
python cli.py read fastapi.tiangolo.com "tutorial"
```

## Python API

Use the scraper programmatically in your Python code:

```python
from scraper import DocumentationScraper

# Initialize scraper
scraper = DocumentationScraper(
    storage_dir="./my_docs",
    max_pages=200,
    delay=0.5
)

# Scrape a documentation site
result = scraper.scrape("https://docs.python.org/3/")

if result['success']:
    print(f"Successfully scraped {result['total_pages']} pages")
    print(f"Stored in: {result['storage_dir']}")

# List all scraped sites
sites = scraper.list_sites()
print(f"Available sites: {sites}")

# Get site information
info = scraper.get_site_info("docs.python.org")
print(f"Total pages: {info['total_pages']}")

# Search content
results = scraper.search("docs.python.org", "decorator")
for result in results:
    print(f"{result['title']}: {result['context']}")

# Read a specific page
content = scraper.get_page("docs.python.org", "index_12345678.md")
print(content)
```

## Storage Structure

Documentation is stored in the following structure:

```
scraped_docs/
├── docs.python.org/
│   ├── index.json           # Site index with metadata
│   ├── index_abc12345.md    # Individual pages as Markdown
│   ├── tutorial_def67890.md
│   └── ...
├── fastapi.tiangolo.com/
│   ├── index.json
│   └── ...
```

Each Markdown file includes:
- YAML frontmatter with title and URL
- Clean, formatted content
- No navigation, ads, or other clutter

## How It Works

1. **Crawling**:
   - First tries to find and parse `sitemap.xml`
   - Falls back to recursive crawling if no sitemap
   - Stays within the same domain
   - Respects rate limits

2. **Content Extraction**:
   - Identifies main content area using common selectors
   - Removes navigation, footers, sidebars, ads
   - Cleans up scripts, styles, and comments

3. **Markdown Conversion**:
   - Converts HTML to clean Markdown
   - Preserves code blocks, links, and formatting
   - Removes excessive whitespace

4. **Storage**:
   - Saves each page as a separate Markdown file
   - Creates an index with metadata
   - Uses URL-based filenames with hash for uniqueness

## Configuration

### Custom Storage Location

```bash
python cli.py scrape https://docs.example.com --storage-dir ~/my-docs
```

### Adjust Crawling Behavior

```bash
# Scrape more pages
python cli.py scrape https://docs.example.com --max-pages 1000

# Slower crawling (more respectful)
python cli.py scrape https://docs.example.com --delay 2.0
```

## Advanced Usage

### Scraping Multiple Sites

```bash
python cli.py scrape https://docs.python.org/3/
python cli.py scrape https://fastapi.tiangolo.com/
python cli.py scrape https://flask.palletsprojects.com/
```

### Batch Operations

Create a script to scrape multiple sites:

```python
from scraper import DocumentationScraper

sites = [
    "https://docs.python.org/3/",
    "https://fastapi.tiangolo.com/",
    "https://flask.palletsprojects.com/"
]

scraper = DocumentationScraper()

for site in sites:
    print(f"\nScraping {site}...")
    result = scraper.scrape(site)
    if result['success']:
        print(f"✓ Success: {result['total_pages']} pages")
    else:
        print(f"✗ Failed: {result['error']}")
```

## Troubleshooting

### No pages found

- Check if the URL is correct and accessible
- Some sites may block automated access (check robots.txt)
- Try increasing `--delay` to be more respectful

### Content extraction issues

- Some documentation sites have unusual HTML structures
- You may need to customize the content selectors in `extractor.py`

### Rate limiting

- Increase `--delay` to reduce request frequency
- Some sites may temporarily block rapid requests

## Contributing

Contributions are welcome! Areas for improvement:

- Support for authentication (for private docs)
- Better content extraction for specific doc platforms
- PDF export functionality
- Vector embeddings for semantic search
- Web UI for browsing scraped docs

## License

MIT License - Feel free to use and modify as needed.

## Use Cases

- **Offline Documentation**: Read docs without internet access
- **AI Training**: Prepare documentation for fine-tuning or RAG systems
- **Documentation Analysis**: Analyze documentation structure and content
- **Archival**: Preserve documentation versions
- **Search Enhancement**: Better search than many built-in doc search tools
