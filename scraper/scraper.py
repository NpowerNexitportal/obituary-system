import time
from datetime import datetime
from trends import get_trending_obituary_keywords
from parser import search_and_extract
from rewriter import rewrite_content
from db import Database

def main():
    print(f"[{datetime.utcnow()}] Starting Obituary Scraper...")
    
    db = Database()
    
    # 1. Fetch trends
    keywords = get_trending_obituary_keywords()
    print(f"Found {len(keywords)} trending keywords: {keywords}")
    
    for keyword in keywords:
        print(f"Processing keyword: {keyword}")
        
        # 2. Scrape content
        results = search_and_extract(keyword)
        
        for result in results:
            raw_text = result['raw_content']
            source_url = result['source_url']
            
            # 3. Rewrite and extract structured data
            article_data = rewrite_content(raw_text, name_hint=keyword)
            
            article_data['source_url'] = source_url
            article_data['created_at'] = datetime.utcnow()
            article_data['hash'] = db.generate_hash(article_data['content'])
            
            # 4. Save to MongoDB
            inserted_id = db.insert_obituary(article_data)
            
            if inserted_id:
                print(f" -> Inserted new obituary: {article_data['title']} ({inserted_id})")
            
            # Sleep to be polite and avoid rate limits
            time.sleep(2)

if __name__ == "__main__":
    main()
