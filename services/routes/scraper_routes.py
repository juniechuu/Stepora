from flask import Blueprint, jsonify, request
import requests
from bs4 import BeautifulSoup
import re

# Create blueprint for scraper routes
scraper_bp = Blueprint('scraper', __name__)

@scraper_bp.route('/scrape-wikihow', methods=['POST'])
def scrape_wikihow():
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Search WikiHow
        search_url = f"https://www.wikihow.com/wikiHowTo?search={query.replace(' ', '+')}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        print(f"Searching WikiHow for: {query}")
        search_response = requests.get(search_url, headers=headers, timeout=10)
        search_soup = BeautifulSoup(search_response.content, 'html.parser')
        
        # Get first article link
        article_link = search_soup.find('a', class_='result_link')
        if not article_link:
            return jsonify({'error': 'No WikiHow article found for this query'}), 404
        
        article_url = article_link.get('href')
        if not article_url.startswith('http'):
            article_url = 'https://www.wikihow.com' + article_url
            
        print(f"Found article: {article_url}")
        
        # Scrape the article
        article_response = requests.get(article_url, headers=headers, timeout=10)
        article_soup = BeautifulSoup(article_response.content, 'html.parser')
        
        # Extract title
        title_elem = article_soup.find('h1', class_='mw-headline')
        if not title_elem:
            title_elem = article_soup.find('h1')
        title_text = title_elem.text.strip() if title_elem else query
        
        # Extract introduction
        intro_text = ''
        intro_div = article_soup.find('div', id='intro')
        if intro_div:
            intro_p = intro_div.find('p')
            intro_text = intro_p.text.strip() if intro_p else ''
        
        # Extract prerequisites
        prerequisites = []
        things_section = article_soup.find('div', id='thingsyoullneed_anchor')
        if things_section:
            prereq_items = things_section.find_all('li')
            prerequisites = [item.text.strip() for item in prereq_items[:5]]
        
        # Extract steps
        steps = []
        
        # Method 1: Try standard step divs
        step_sections = article_soup.find_all('div', class_='step')
        
        if not step_sections:
            # Method 2: Try by ID pattern
            step_sections = article_soup.find_all('div', id=re.compile(r'step_id_\d+'))
        
        if not step_sections:
            # Method 3: Try steps_list class
            steps_list = article_soup.find('div', class_='steps_list_2')
            if not steps_list:
                steps_list = article_soup.find('ol', class_='steps_list')
            if steps_list:
                step_sections = steps_list.find_all(['div', 'li'], recursive=False)
        
        if not step_sections:
            # Method 4: Try to find any li elements in the main content
            content = article_soup.find('div', id='mw-content-text')
            if content:
                step_sections = content.find_all('li', limit=20)
        
        print(f"Found {len(step_sections)} step sections")
        
        for idx, step_div in enumerate(step_sections[:15], 1):  # Limit to 15 steps
            # Extract step title and description
            step_title = f"Step {idx}"
            step_text = ''
            tips = []
            
            # Try to find title in bold
            step_title_elem = step_div.find('b')
            if step_title_elem:
                step_title = step_title_elem.get_text(strip=True)
                # Remove the title from consideration when extracting description
                step_title_elem.extract()
            
            # Get the remaining text as description
            step_text = step_div.get_text(separator=' ', strip=True)
            
            # Clean up the text
            step_text = re.sub(r'\s+', ' ', step_text).strip()
            
            # Skip if text is too short (likely not a real step)
            if len(step_text) < 10:
                continue
            
            # Look for tips in the step
            tip_div = step_div.find('div', class_='tips')
            if not tip_div:
                tip_div = step_div.find('ul', class_='tips')
            
            if tip_div:
                tip_items = tip_div.find_all('li')
                tips = [tip.get_text(strip=True) for tip in tip_items[:3]]
            
            steps.append({
                'title': step_title,
                'description': step_text,
                'tips': tips if tips else None
            })
        
        print(f"Extracted {len(steps)} valid steps")
        
        # If still no steps found, try a more aggressive approach
        if not steps:
            # Look for numbered lists in the content
            content = article_soup.find('div', id='mw-content-text')
            if content:
                all_lists = content.find_all(['ol', 'ul'])
                for list_elem in all_lists:
                    list_items = list_elem.find_all('li', recursive=False)
                    if len(list_items) >= 3:  # Likely a steps list
                        for idx, item in enumerate(list_items[:15], 1):
                            text = item.get_text(separator=' ', strip=True)
                            if len(text) >= 20:  # Meaningful content
                                steps.append({
                                    'title': f"Step {idx}",
                                    'description': text,
                                    'tips': None
                                })
                        if steps:
                            break
        
        # If no steps found, return error
        if not steps:
            return jsonify({'error': 'Could not extract steps from WikiHow article. The page structure may have changed.'}), 500
        
        # Extract related links
        related_links = []
        related_section = article_soup.find('div', id='related_articles')
        if related_section:
            related_items = related_section.find_all('a', limit=5)
            for link in related_items:
                link_url = link.get('href')
                if link_url and not link_url.startswith('http'):
                    link_url = 'https://www.wikihow.com' + link_url
                related_links.append({
                    'title': link.text.strip(),
                    'url': link_url
                })
        
        # Calculate read time (rough estimate: 1 step = 1 minute)
        read_time = max(3, len(steps))
        
        return jsonify({
            'title': title_text,
            'introduction': intro_text if intro_text else f"Learn {title_text.lower()} with this comprehensive guide from WikiHow.",
            'prerequisites': prerequisites if prerequisites else None,
            'steps': steps,
            'conclusion': f"By following these steps, you should now know {title_text.lower()}. Practice makes perfect!",
            'relatedLinks': related_links if related_links else None,
            'readTime': read_time,
            'difficulty': 'Intermediate',
            'source': article_url,
            'status': 'success'
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. WikiHow may be slow or unreachable.'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        print(f"Error scraping WikiHow: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
