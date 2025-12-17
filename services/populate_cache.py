"""
Script to populate the cache database with 100 articles
Run this script to automatically search and cache articles
"""
import requests
import time
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:5000/api"
DELAY_BETWEEN_REQUESTS = 3  # seconds to wait between requests

# 100 diverse search queries for how-to guides
SEARCH_QUERIES = [
    # Technology & Programming
    "How to build a website from scratch",
    "How to learn Python programming",
    "How to create a mobile app",
    "How to set up a home network",
    "How to build a gaming PC",
    "How to code in JavaScript",
    "How to use Git and GitHub",
    "How to create a blog",
    "How to learn data science",
    "How to start with machine learning",
    
    # Business & Career
    "How to start a small business",
    "How to write a resume",
    "How to prepare for a job interview",
    "How to negotiate salary",
    "How to create a business plan",
    "How to start freelancing",
    "How to market on social media",
    "How to improve public speaking",
    "How to manage time effectively",
    "How to build a personal brand",
    
    # Creative & Arts
    "How to draw portraits",
    "How to play guitar for beginners",
    "How to write a novel",
    "How to take professional photos",
    "How to edit videos",
    "How to paint with watercolors",
    "How to design a logo",
    "How to start a YouTube channel",
    "How to write a song",
    "How to learn digital art",
    
    # Health & Fitness
    "How to lose weight healthily",
    "How to build muscle at home",
    "How to start running",
    "How to do yoga for beginners",
    "How to meditate daily",
    "How to improve sleep quality",
    "How to eat healthy on a budget",
    "How to train for a marathon",
    "How to reduce stress naturally",
    "How to improve posture",
    
    # Home & Garden
    "How to grow vegetables in a garden",
    "How to decorate a small apartment",
    "How to organize a closet",
    "How to paint a room",
    "How to fix a leaky faucet",
    "How to start composting",
    "How to create a home office",
    "How to clean a house efficiently",
    "How to arrange furniture",
    "How to care for houseplants",
    
    # Food & Cooking
    "How to bake bread from scratch",
    "How to cook pasta perfectly",
    "How to make pizza at home",
    "How to prepare sushi",
    "How to grill steak",
    "How to meal prep for the week",
    "How to make coffee like a barista",
    "How to bake chocolate chip cookies",
    "How to cook rice properly",
    "How to make smoothies",
    
    # Personal Development
    "How to learn a new language",
    "How to improve memory",
    "How to read faster",
    "How to develop good habits",
    "How to overcome procrastination",
    "How to set and achieve goals",
    "How to boost confidence",
    "How to be more productive",
    "How to practice gratitude",
    "How to improve communication skills",
    
    # Finance & Money
    "How to create a budget",
    "How to save money effectively",
    "How to invest in stocks",
    "How to start investing",
    "How to pay off debt",
    "How to build credit",
    "How to start a side hustle",
    "How to file taxes",
    "How to create passive income",
    "How to plan for retirement",
    
    # Education & Learning
    "How to study effectively",
    "How to take better notes",
    "How to prepare for exams",
    "How to write an essay",
    "How to improve writing skills",
    "How to learn math concepts",
    "How to research effectively",
    "How to memorize information",
    "How to speed read",
    "How to cite sources properly",
    
    # Lifestyle & Social
    "How to make new friends",
    "How to plan a wedding",
    "How to travel on a budget",
    "How to pack for a trip",
    "How to learn photography",
    "How to start journaling",
    "How to reduce screen time",
    "How to be a better listener",
    "How to host a dinner party",
    "How to improve relationships"
]

def search_and_cache_article(query, index, total):
    """Send a search request to cache an article"""
    try:
        print(f"\n[{index}/{total}] Searching: '{query}'")
        
        # First, check if it exists in cache
        check_response = requests.post(
            f"{API_BASE_URL}/cache/check",
            json={
                "search_query": query,
                "search_type": "teen-adult",
                "similarity_threshold": 0.85
            },
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if check_response.status_code == 200:
            cache_data = check_response.json()
            if cache_data.get('cached'):
                print(f"⊙ Already cached: '{query}'")
                return True
        
        # Generate the article using OpenAI
        prompt = f"""Write a comprehensive, professional how-to article about: {query}. 

Format the response EXACTLY as follows:

TITLE: [Clear, descriptive title]

INTRODUCTION: [Brief introduction explaining what will be covered and why it's useful]

PREREQUISITES: [List any prerequisites, one per line, or write "None"]

STEPS:
STEP 1: [Step title]
[Detailed description]
TIPS: [Optional tips, one per line]

STEP 2: [Step title]
[Detailed description]
TIPS: [Optional tips, one per line]

[Continue for all steps...]

CONCLUSION: [Summary and final thoughts]

RELATED: [3-5 related topics or resources, one per line]"""

        ai_response = requests.post(
            f"{API_BASE_URL}/ai/openai",
            json={"prompt": prompt},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if ai_response.status_code != 200:
            print(f"✗ AI Failed (Status {ai_response.status_code})")
            return False
        
        article_response = ai_response.json().get('response', '')
        
        # Store in cache
        cache_response = requests.post(
            f"{API_BASE_URL}/cache/store",
            json={
                "search_query": query,
                "search_type": "teen-adult",
                "response": article_response
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if cache_response.status_code == 201:
            print(f"✓ Success! Cached article for: '{query}'")
            return True
        else:
            print(f"✗ Cache Failed (Status {cache_response.status_code})")
            return False
            
    except requests.exceptions.Timeout:
        print(f"✗ Timeout: Request took too long")
        return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection Error: Could not reach server")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Cache Population Script")
    print("=" * 60)
    print(f"Target: {len(SEARCH_QUERIES)} articles")
    print(f"Delay between requests: {DELAY_BETWEEN_REQUESTS} seconds")
    print(f"Estimated time: {(len(SEARCH_QUERIES) * DELAY_BETWEEN_REQUESTS) / 60:.1f} minutes")
    print("=" * 60)
    
    input("\nPress Enter to start caching articles...")
    
    successful = 0
    failed = 0
    start_time = time.time()
    
    for index, query in enumerate(SEARCH_QUERIES, 1):
        success = search_and_cache_article(query, index, len(SEARCH_QUERIES))
        
        if success:
            successful += 1
        else:
            failed += 1
        
        # Progress update every 10 articles
        if index % 10 == 0:
            elapsed = time.time() - start_time
            print(f"\n--- Progress: {index}/{len(SEARCH_QUERIES)} ---")
            print(f"Successful: {successful} | Failed: {failed}")
            print(f"Elapsed time: {elapsed / 60:.1f} minutes")
            print(f"Average time per article: {elapsed / index:.1f} seconds")
        
        # Wait between requests (except for the last one)
        if index < len(SEARCH_QUERIES):
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Final summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("CACHE POPULATION COMPLETE!")
    print("=" * 60)
    print(f"Total articles processed: {len(SEARCH_QUERIES)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful / len(SEARCH_QUERIES) * 100):.1f}%")
    print(f"Total time: {total_time / 60:.1f} minutes")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
