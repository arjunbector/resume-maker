import re

def parse_questions(response_text: str) -> list:
    """
    Parse questions from AI response text and return a clean list of questions

    Args:
        response_text: The raw response text containing numbered questions

    Returns:
        List of question strings
    """
    questions_list = []

    # Split by lines and process each line
    lines = response_text.strip().split('\n')

    for line in lines:
        line = line.strip()

        # Skip empty lines and category headers
        if not line or line.endswith(':') or line.startswith('**') or line.startswith('#'):
            continue

        # Remove numbering (1., 2., etc.) and clean up
        # Handle various numbering formats: "1.", "1)", "1 -", etc.
        cleaned_line = re.sub(r'^\d+[\.\)\-\s]+', '', line).strip()

        # Remove any remaining markdown or formatting
        cleaned_line = re.sub(r'^\*+\s*', '', cleaned_line).strip()
        cleaned_line = re.sub(r'\*\*', '', cleaned_line).strip()

        # Only add non-empty questions
        if cleaned_line:
            # Ensure it's a question (ends with ?)
            if not cleaned_line.endswith('?'):
                cleaned_line += '?'
            questions_list.append(cleaned_line)

    # If we couldn't parse properly, try a simpler approach
    if not questions_list:
        # Look for lines that look like questions
        for line in lines:
            line = line.strip()
            if '?' in line:
                # Clean up any numbering
                cleaned_line = re.sub(r'^\d+[\.\)\-\s]+', '', line).strip()
                questions_list.append(cleaned_line)

    return questions_list
