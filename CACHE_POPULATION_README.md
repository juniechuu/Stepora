# Cache Population Script

This script automatically populates your database with 100 cached articles by making sequential searches to the teen-adult tutorial API.

## Prerequisites

1. Flask backend must be running on `http://127.0.0.1:5000`
2. Python 3 installed with `requests` library

## Installation

Install the required package:
```bash
pip install requests
```

## Usage

1. **Start your Flask backend first:**
   ```bash
   cd services
   python app.py
   ```

2. **In a new terminal, run the cache population script:**
   ```bash
   cd services
   python populate_cache.py
   ```

3. The script will:
   - Display the number of articles to cache
   - Show estimated completion time
   - Wait for your confirmation (Press Enter)
   - Make API calls with 3-second delays between each
   - Show progress updates every 10 articles
   - Display a final summary

## Configuration

You can modify these variables in `populate_cache.py`:

- `DELAY_BETWEEN_REQUESTS`: Time to wait between API calls (default: 3 seconds)
- `SEARCH_QUERIES`: List of search queries to cache (default: 100 queries)
- `API_BASE_URL`: Backend API URL (default: http://127.0.0.1:5000/api)

## Example Output

```
============================================================
Cache Population Script
============================================================
Target: 100 articles
Delay between requests: 3 seconds
Estimated time: 5.0 minutes
============================================================

Press Enter to start caching articles...

[1/100] Searching: 'How to build a website from scratch'
✓ Success! Cached article for: 'How to build a website from scratch'

[2/100] Searching: 'How to learn Python programming'
✓ Success! Cached article for: 'How to learn Python programming'

--- Progress: 10/100 ---
Successful: 10 | Failed: 0
Elapsed time: 0.5 minutes
Average time per article: 3.2 seconds
```

## Categories Included

The script includes diverse queries across:
- Technology & Programming (10 queries)
- Business & Career (10 queries)
- Creative & Arts (10 queries)
- Health & Fitness (10 queries)
- Home & Garden (10 queries)
- Food & Cooking (10 queries)
- Personal Development (10 queries)
- Finance & Money (10 queries)
- Education & Learning (10 queries)
- Lifestyle & Social (10 queries)

## Notes

- Total estimated time: ~5-10 minutes (depending on API response times)
- The script automatically handles errors and continues with remaining articles
- Press Ctrl+C to stop the script at any time
- Cached articles will be stored in your SQLite database
- You can run the script multiple times safely (it will just update existing cache entries)
