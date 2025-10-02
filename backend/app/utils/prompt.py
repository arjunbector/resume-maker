from models import JobQuestionsRequest


def generate_prompt(req: JobQuestionsRequest) -> str:
    """Generate a prompt for the LLM based on the JobQuestionsRequest"""

    prompt = f"""
Tool Call: get_website_content with the following url {req.company_url}

Read a job description, job role, and company summary, then generate a tailored set of concise, information-gathering questions for the user. The goal is to collect all the specific details needed to craft a strong, customized resume for this role.

**Job Role:** {req.job_role}
**Company:** {req.company_name}
**Job Description:** {req.job_description}
**Company Details:** Use the company details fetched from the website by the get_website_content tool call.
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
Produce a numbered list of concise, user-facing questions. Generate a maximum of 10 questions total.

Questions:
    """

    return prompt