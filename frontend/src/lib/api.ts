/**
 * API utility functions for making API calls
 */

/**
 * Compare skills with job requirements
 * @param sessionId - The session ID for the resume
 * @returns Promise with the comparison result
 * @throws Error if the API call fails
 */
export async function compareSkills(sessionId: string): Promise<any> {
  if (!sessionId) {
    throw new Error("Session ID is required");
  }
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/ai/compare?session_id=${sessionId}`,
    {
      method: "POST",
      credentials: "include",
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || "Failed to compare skills");
  }

  return response.json();
}

/**
 * Generate questionnaire based on job description and skills comparison
 * @param sessionId - The session ID for the resume
 * @returns Promise with the questionnaire result
 * @throws Error if the API call fails
 */
export async function generateQuestionnaire(sessionId: string): Promise<any> {
  if (!sessionId) {
    throw new Error("Session ID is required");
  }

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/ai/generate-questionnaire?session_id=${sessionId}`,
    {
      method: "POST",
      credentials: "include",
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || "Failed to generate questionnaire");
  }

  return response.json();
}

