from .smolagents_pipeline import pipeline
from .website_summary_pipeline import website_summary_pipeline
import logging

logger = logging.getLogger(__name__)

class JobQuestionsPipeline:
    def __init__(self):
        self.llm_pipeline = pipeline
        self.website_pipeline = website_summary_pipeline
    
    def generate_questions(self, job_role: str, company_url: str, job_description: str) -> dict:
        """
        Generate tailored questions based on job role, company URL, and job description
        
        Args:
            job_role: The job title/role being applied for
            company_url: The company website URL to scrape for context
            job_description: Full job description text
        
        Returns:
            Dictionary containing generated questions and metadata
        """
        try:
            # Step 1: Get company information from website
            logger.info(f"Scraping company website: {company_url}")
            company_summary_result = self.website_pipeline.summarize_website(company_url, "general")
            
            if 'error' in company_summary_result:
                logger.warning(f"Failed to scrape company website: {company_summary_result['error']}")
                company_summary = f"Unable to gather company information from {company_url}"
                company_name = company_url
            else:
                company_summary = company_summary_result.get('ai_summary', 'No summary available')
                # Extract company name from scraped data
                scraped_data = company_summary_result.get('scraped_data', {})
                company_name = scraped_data.get('title', company_url)
                if company_name:
                    # Clean up title to get company name
                    company_name = company_name.split(' - ')[0].split(' | ')[0].strip()
            
            # Step 2: Create the prompt with company summary
            prompt = self._create_questions_prompt(job_role, company_name, company_summary, job_description)
            
            logger.info(f"Generating tailored questions for {job_role} at {company_name}")
            
            # Step 3: Get AI-generated questions
            questions_text = self.llm_pipeline.process_prompt(prompt)
            
            # Step 4: Parse questions into list format and limit to 10
            questions_list = self._parse_questions_to_list(questions_text)
            
            return {
                'job_role': job_role,
                'company_url': company_url,
                'company_name': company_name,
                'company_summary': company_summary,
                'questions': questions_list,
                'total_questions': len(questions_list),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error generating questions for {job_role} at {company_url}: {str(e)}")
            return {
                'job_role': job_role,
                'company_url': company_url,
                'error': f'Questions generation failed: {str(e)}',
                'success': False
            }
    
    def _create_questions_prompt(self, job_role: str, company_name: str, company_summary: str, job_description: str) -> str:
        """Create the prompt using the provided template"""
        
        prompt = f"""Read a job description, job role, and company summary, then generate a tailored set of concise, information-gathering questions for the user. The goal is to collect all the specific details needed to craft a strong, customized resume for this role.

**Job Role:** {job_role}
**Company:** {company_name}
**Company Summary:** {company_summary}
**Job Description:**
{job_description}

**Instructions:**

1. Analyze context: Carefully review the job description, job role, and company summary to identify required skills, experiences, and cultural fit.
2. Identify gaps: Determine what information is missing from the user that would demonstrate alignment with these requirements.
3. Generate tailored questions: Write clear, one-line questions that the user can answer briefly. Do not ask open-ended or "explain in detail" type questions. Each question should request a specific fact, number, or short statement.

   * Relevant skills and technical expertise (e.g., "Which programming languages are you proficient in?")
   * Experience and achievements in similar roles or industries (e.g., "How many years have you worked in quantitative research?")
   * Domain-specific knowledge (e.g., "Which risk models have you implemented before?")
   * Education, certifications, and training (e.g., "What is your highest degree and field of study?")
   * Soft skills, leadership, and collaboration (e.g., "Have you managed a team before? If yes, how many people?")
   * Unique contributions or differentiators (e.g., "Have you won any hackathons or awards?")

4. Make them role-specific: Adapt the questions to the company's field. For example:

   * For a quant finance firm: "How many years of experience do you have in financial modeling?"
   * For a Web3 startup: "Have you deployed smart contracts on Ethereum or other blockchains?"
   * For a healthtech company: "Have you worked with clinical datasets before?"

5. Prioritize clarity and brevity: Ensure all questions can be answered in a short, direct response (one line).

**Output format:**
Produce a numbered list of concise, user-facing questions organized by category (e.g., Technical Skills, Experience, Education, Achievements, Culture Fit). Generate a maximum of 10 questions total.

Questions:"""
        
        return prompt
    
    def _parse_questions_to_list(self, questions_text: str) -> list:
        """Parse the AI-generated questions text into a clean list format"""
        questions_list = []
        
        # Split by lines and process each line
        lines = questions_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and category headers
            if not line or line.endswith(':') or line.startswith('**') or line.startswith('#'):
                continue
            
            # Remove numbering (1., 2., etc.) and clean up
            # Handle various numbering formats: "1.", "1)", "1 -", etc.
            import re
            cleaned_line = re.sub(r'^\d+[\.\)\-\s]+', '', line).strip()
            
            # Remove any remaining markdown or formatting
            cleaned_line = re.sub(r'^\*+\s*', '', cleaned_line).strip()
            cleaned_line = re.sub(r'\*\*', '', cleaned_line).strip()
            
            # Only add non-empty questions and limit to 10
            if cleaned_line and len(questions_list) < 10:
                # Ensure it's a question (ends with ?)
                if not cleaned_line.endswith('?'):
                    cleaned_line += '?'
                questions_list.append(cleaned_line)
        
        # If we couldn't parse properly, try a simpler approach
        if not questions_list:
            # Look for lines that look like questions
            for line in lines:
                line = line.strip()
                if '?' in line and len(questions_list) < 10:
                    # Clean up any numbering
                    cleaned_line = re.sub(r'^\d+[\.\)\-\s]+', '', line).strip()
                    questions_list.append(cleaned_line)
        
        return questions_list[:10]  # Ensure max 10 questions

job_questions_pipeline = JobQuestionsPipeline()