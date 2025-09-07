from .scraper import scraper
from .smolagents_pipeline import pipeline
import logging

logger = logging.getLogger(__name__)

class WebsiteSummaryPipeline:
    def __init__(self):
        self.scraper = scraper
        self.llm_pipeline = pipeline
    
    def summarize_website(self, url: str, summary_type: str = "general") -> dict:
        """
        Pipeline that scrapes a website and summarizes its content using Gemini LLM
        
        Args:
            url: The website URL to scrape and summarize
            summary_type: Type of summary ('general', 'key_points', 'technical', 'brief')
        
        Returns:
            Dictionary containing the original scraped data and the AI summary
        """
        try:
            # Scrape the website
            logger.info(f"Scraping website: {url}")
            scraped_data = self.scraper.scrape_website(url)
            
            # Check if scraping failed
            if 'error' in scraped_data:
                return {
                    'url': url,
                    'error': scraped_data['error'],
                    'step_failed': 'scraping'
                }
            
            # Prepare content for summarization
            content_to_summarize = self._prepare_content_for_summary(scraped_data)
            
            if not content_to_summarize.strip():
                return {
                    'url': url,
                    'error': 'No meaningful content found to summarize',
                    'step_failed': 'content_preparation',
                    'scraped_data': scraped_data
                }
            
            # Generate summary prompt based on type
            summary_prompt = self._generate_summary_prompt(content_to_summarize, summary_type, url)
            
            # Get AI summary
            logger.info(f"Generating {summary_type} summary for: {url}")
            ai_summary = self.llm_pipeline.process_prompt(summary_prompt)
            
            return {
                'url': url,
                'summary_type': summary_type,
                'ai_summary': ai_summary,
                'scraped_data': scraped_data,
                'content_length': len(content_to_summarize),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error in website summary pipeline for {url}: {str(e)}")
            return {
                'url': url,
                'error': f'Pipeline failed: {str(e)}',
                'step_failed': 'pipeline_execution'
            }
    
    def _prepare_content_for_summary(self, scraped_data: dict) -> str:
        """Prepare scraped content for summarization by combining relevant parts"""
        content_parts = []
        
        # Add title
        if scraped_data.get('title'):
            content_parts.append(f"Title: {scraped_data['title']}")
        
        # Add meta description
        if scraped_data.get('meta_description'):
            content_parts.append(f"Description: {scraped_data['meta_description']}")
        
        # Add headings
        if scraped_data.get('headings'):
            headings_text = "\n".join([f"H{h['level']}: {h['text']}" for h in scraped_data['headings'][:10]])  # Limit to first 10 headings
            content_parts.append(f"Headings:\n{headings_text}")
        
        # Add paragraphs (limit to prevent token overflow)
        if scraped_data.get('paragraphs'):
            paragraphs_text = "\n".join(scraped_data['paragraphs'][:15])  # Limit to first 15 paragraphs
            content_parts.append(f"Content:\n{paragraphs_text}")
        
        # If no structured content, use clean text (truncated)
        if not content_parts and scraped_data.get('text_content'):
            clean_text = scraped_data['text_content'][:5000]  # Limit to 5000 characters
            content_parts.append(f"Text Content:\n{clean_text}")
        
        return "\n\n".join(content_parts)
    
    def _generate_summary_prompt(self, content: str, summary_type: str, url: str) -> str:
        """Generate appropriate prompt based on summary type"""
        
        base_prompt = f"Please analyze and summarize the following website content from {url}:\n\n{content}\n\n"
        
        summary_instructions = {
            "general": "Provide a comprehensive summary covering the main topics, purpose, and key information of this website.",
            "key_points": "Extract and list the most important key points and takeaways from this website in bullet format.",
            "technical": "Focus on technical aspects, features, specifications, and technical details mentioned on this website.",
            "brief": "Provide a very brief 2-3 sentence summary of what this website is about."
        }
        
        instruction = summary_instructions.get(summary_type, summary_instructions["general"])
        
        return f"{base_prompt}{instruction}\n\nSummary:"

website_summary_pipeline = WebsiteSummaryPipeline()