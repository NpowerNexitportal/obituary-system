import requests
from bs4 import BeautifulSoup
import feedparser
from duckduckgo_search import DDGS
from urllib.parse import urlparse
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def discover_rss_feeds(keyword):
    """
    Uses DuckDuckGo to search for obituary blogs on specific domains,
    then automatically discovers their RSS feeds.
    Prioritizes .site -> .today -> .com.ng. Gets max 3 feeds total.
    """
    found_feeds = []
    base_urls = set()
    
    # Priority queues
    queries = [
        f"{keyword} site:.site",
        f"{keyword} site:.today",
        f"{keyword} site:.com.ng"
    ]
    
    for query in queries:
        if len(found_feeds) >= 3:
            break
            
        try:
            print(f"Searching for new blogs using query: {query}")
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=10))
                
                for res in results:
                    url = res.get('href')
                    if url:
                        parsed_uri = urlparse(url)
                        base_url = f"{parsed_uri.scheme}://{parsed_uri.netloc}"
                        
                        if base_url not in base_urls:
                            base_urls.add(base_url)
                            print(f"Probing {base_url} for RSS feeds...")
                            feed_url = find_rss_feed(base_url)
                            if feed_url and feed_url not in found_feeds:
                                found_feeds.append(feed_url)
                                print(f" -> Found Feed: {feed_url}")
                                
                    if len(found_feeds) >= 3:
                        break
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            
    return found_feeds[:3]

def find_rss_feed(base_url):
    """
    Probes a website to find its RSS feed URL.
    """
    common_paths = ['/feed', '/rss', '/feed.xml', '/index.xml', '/feed/']
    
    # 1. Try parsing the HTML head for RSS link tags first (most reliable)
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for <link rel="alternate" type="application/rss+xml">
            link = soup.find('link', type='application/rss+xml')
            if link and link.get('href'):
                href = link['href']
                if href.startswith('/'):
                    return base_url + href
                return href
    except:
        pass
        
    # 2. Try common paths manually
    for path in common_paths:
        test_url = base_url + path
        try:
            resp = requests.get(test_url, headers=HEADERS, timeout=5)
            if resp.status_code == 200 and ('xml' in resp.headers.get('Content-Type', '') or 'rss' in resp.text[:200].lower()):
                return test_url
        except:
            pass
            
    return None

def fetch_rss_articles(feed_url, limit=3):
    """
    Parses an RSS feed and returns the latest articles.
    """
    articles = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:limit]:
            content = ""
            if hasattr(entry, 'content'):
                content = entry.content[0].value
            elif hasattr(entry, 'summary'):
                content = entry.summary
            elif hasattr(entry, 'description'):
                content = entry.description
                
            # Clean HTML from content
            clean_content = BeautifulSoup(content, 'html.parser').get_text(separator=' ', strip=True)
            
            if len(clean_content) > 100:
                articles.append({
                    "source_url": entry.link,
                    "raw_content": clean_content,
                    "title": entry.title
                })
    except Exception as e:
        print(f"Error reading feed {feed_url}: {e}")
        
    return articles

def search_and_extract(keyword):
    """
    Main entrypoint: Discovers feeds via search and extracts their latest articles.
    """
    results = []
    feeds = discover_rss_feeds(keyword)
    print(f"Discovered {len(feeds)} RSS feeds for keyword '{keyword}'. Extracting content...")
    
    for feed in feeds:
        articles = fetch_rss_articles(feed, limit=2)
        for art in articles:
            art['keyword'] = keyword
            results.append(art)
            
    return results
