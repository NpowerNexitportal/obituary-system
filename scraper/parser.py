import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def search_and_extract(keyword):
    """
    Searches Google Search for the keyword and extracts text content from top results,
    filtering for specific domain extensions (.com.ng, .sites, .today).
    """
    results = []
    try:
        from urllib.parse import urlparse
        # Use Google Search URL
        query = keyword.replace(' ', '+')
        url = f"https://www.google.com/search?q={query}"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        # Extract result links from Google search page
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            # Google often redirects URLs via /url?q=
            if href.startswith('/url?q='):
                href = href.split('/url?q=')[1].split('&')[0]
                
            if href.startswith('http'):
                domain = urlparse(href).netloc.lower()
                
                # Filter domains based on user requirements (.com.ng, .sites, .today)
                if domain.endswith('.com.ng') or domain.endswith('.sites') or domain.endswith('.site') or domain.endswith('.today'):
                    if href not in links:
                        links.append(href)
                        
            if len(links) >= 5: # Get up to 5 matching links
                break
                
        for link in links:
            content = extract_article_content(link)
            if content:
                results.append({
                    "source_url": link,
                    "raw_content": content,
                    "keyword": keyword
                })
    except Exception as e:
        print(f"Error searching for {keyword}: {e}")
        
    return results

def extract_article_content(url):
    """
    Visits the URL and extracts the main text using basic heuristics.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        # Try to find main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('(content|article|body)', re.I))
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)
            
        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Return only if it has substantial content
        if len(text) > 300:
            return text
            
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        
    return None
