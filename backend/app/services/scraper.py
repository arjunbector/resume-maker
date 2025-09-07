import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_website(self, url: str) -> dict:
        """Scrape content from a website and return structured data"""
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL provided")
            
            # Fetch the webpage
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            content = {
                'url': url,
                'title': self._get_title(soup),
                'meta_description': self._get_meta_description(soup),
                'headings': self._get_headings(soup),
                'paragraphs': self._get_paragraphs(soup),
                'links': self._get_links(soup, url),
                'text_content': self._get_clean_text(soup),
                'status_code': response.status_code
            }
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while scraping {url}: {str(e)}")
            return {'error': f'Request failed: {str(e)}', 'url': url}
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {'error': f'Scraping failed: {str(e)}', 'url': url}
    
    def _get_title(self, soup):
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None
    
    def _get_meta_description(self, soup):
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content').strip() if meta_desc else None
    
    def _get_headings(self, soup):
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text().strip()
                })
        return headings
    
    def _get_paragraphs(self, soup):
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:
                paragraphs.append(text)
        return paragraphs
    
    def _get_links(self, soup, base_url):
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text().strip()
            absolute_url = urljoin(base_url, href)
            links.append({
                'text': text,
                'url': absolute_url
            })
        return links
    
    def _get_clean_text(self, soup):
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

scraper = WebScraper()