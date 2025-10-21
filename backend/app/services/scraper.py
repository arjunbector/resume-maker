import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from smolagents import tool
import json

@tool
def get_website_content(website_url: str) -> str:
    """
    Get the website content by scraping the website

    Args:
        website_url: the url of the website to scrape
    """
    try:
        # Validate URL
        parsed_url = urlparse(website_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return json.dumps({
                'error': 'Invalid URL provided',
                'url': website_url
            })

        # Fetch the webpage
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Set max redirects to 5 to avoid redirect loops
        session.max_redirects = 5

        # Try the request with allow_redirects and verify SSL
        response = session.get(
            website_url,
            timeout=10,
            allow_redirects=True,
            verify=True
        )
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else None

        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc.get('content').strip() if meta_desc else None

        # Extract headings
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text().strip()
                })

        # Extract paragraphs
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:
                paragraphs.append(text)

        # Get clean text content
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)

        # Return JSON blob
        content = {
            'url': website_url,
            'title': title,
            'meta_description': meta_description,
            'headings': headings[:10],  # Limit to first 10 headings
            'paragraphs': paragraphs[:15],  # Limit to first 15 paragraphs
            'text_content': clean_text[:5000],  # Limit to 5000 characters
            'status_code': response.status_code
        }

        return json.dumps(content)

    except requests.exceptions.RequestException as e:
        return json.dumps({
            'error': f'Request failed: {str(e)}',
            'url': website_url
        })
    except Exception as e:
        return json.dumps({
            'error': f'Scraping failed: {str(e)}',
            'url': website_url
        })
