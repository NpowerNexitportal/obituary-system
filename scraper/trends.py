from pytrends.request import TrendReq
import time

def get_trending_obituary_keywords():
    """
    Fetches trending queries related to obituaries in the USA.
    """
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        kw_list = ["obituary", "death"]
        
        # Build payload
        pytrends.build_payload(kw_list, cat=0, timeframe='now 1-d', geo='US', gprop='')
        
        # Get related queries
        related_queries = pytrends.related_queries()
        
        trending_keywords = []
        for kw in kw_list:
            if related_queries.get(kw) and related_queries[kw].get('top') is not None:
                top_queries = related_queries[kw]['top']['query'].tolist()
                # Take top 3-5 from each to limit to 5-10 total
                trending_keywords.extend(top_queries[:3])
                
        # Deduplicate
        trending_keywords = list(set(trending_keywords))
        
        # Limit to max 5-10 keywords per run to optimize performance
        return trending_keywords[:10]
    except Exception as e:
        print(f"Error fetching trends: {e}")
        # Fallback keywords if pytrends fails
        return ["obituary", "death"]
