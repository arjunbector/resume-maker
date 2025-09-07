"use server";

import { gemini } from "@/lib/gemini";
import { canUseAITools } from "@/lib/permissions";
import { getPlanDetails } from "@/lib/subscription";
import { GenerateProjectInfoInput, generateProjectInfoSchema, GenerateSummaryInput, generateSummarySchema, GenerateWorkExperienceInput, generateWorkExperienceSchema, Project, WorkExperience } from "@/lib/validations";
import { auth } from "@clerk/nextjs/server";

export async function generateSummary(input: GenerateSummaryInput) {
    const { userId } = await auth();
    if (!userId) {
        throw new Error("User not authenticated");
    }
    const subscriptionLevel = await getPlanDetails();
    if (!canUseAITools(subscriptionLevel)) {
        throw new Error("You need a premium subscription to use AI tools.");
    }
    const { educations, jobTitle, skills, workExperiences } = generateSummarySchema.parse(input);

    const systemMessage = `
You are a resume summary generation assistant. Your goal is to generate a short, impactful professional summary paragraph that can be placed at the top of a resume.

Instructions:
- Focus on relevant accomplishments, experiences, and strengths aligned with the provided job title.
- Avoid repeating detailed lists of tools, technologies, or job roles already covered in other sections.
- Emphasize career highlights, value offered, and the candidate's unique positioning.
- Keep the tone confident, clear, and professional.
- Keep the summary under 80 words.
- Output only the summary paragraph with no additional formatting, commentary, or instructions.
`;

    const userMessage = `
Generate a resume summary using the information below:

Job Title: ${jobTitle || "N/A"}

Work Experience:
${workExperiences?.map(exp => `
- Position: ${exp.position || "N/A"}
  Company: ${exp.company || "N/A"}
  Duration: ${exp.startDate || "N/A"} to ${exp.endDate || "Present"}
  Description: ${exp.description || "N/A"}
`).join("\n")}

Education:
${educations?.map(edu => `
- Degree: ${edu.degree || "N/A"}
  School: ${edu.school || "N/A"}
  Duration: ${edu.startDate || "N/A"} to ${edu.endDate || "Present"}
  Marks: ${edu.marks || "N/A"}
`).join("\n")}

Skills: ${skills}
`;

    const response = await gemini.models.generateContent({
        model: "gemini-2.0-flash",
        contents: userMessage,
        config: {
            systemInstruction: systemMessage,
        },
    });
    const aiResponse = response.text;
    if (!aiResponse) throw new Error("Failed to generate summary");
    return aiResponse;
}

export async function generateWorkExperience(input: GenerateWorkExperienceInput) {
    const { userId } = await auth();
    if (!userId) {
        throw new Error("User not authenticated");
    }
    const subscriptionLevel = await getPlanDetails();
    if (!canUseAITools(subscriptionLevel)) {
        throw new Error("You need a premium subscription to use AI tools.");
    }
    const { description } = generateWorkExperienceSchema.parse(input);
    const systemMessage = `
You are a resume experience entry generator AI.
Use the description provided by the user to return one formatted work experience entry.

Return the response using the following structure:

Job title: <jobTitle>
Company: <companyName>
Start date: <YYYY-MM-DD> (if available)
End date: <YYYY-MM-DD> (if available)
Description:
• Point 1
• Point 2
• Point 3

Use professional bullet points that emphasize outcomes, responsibilities, or achievements inferred from the role. Do not add any commentary, explanation, or extra formatting.
`;

    const userMessage = `
Based on the following input, generate a work experience entry:
${description}
`;

    const response = await gemini.models.generateContent({
        model: "gemini-2.0-flash",
        contents: userMessage,
        config: {
            systemInstruction: systemMessage,
        },
    });
    const aiResponse = response.text;
    if (!aiResponse) throw new Error("Failed to generate summary");

    const position = aiResponse.match(/Job title:\s*(.*)/i)?.[1]?.trim() || "";
    const company = aiResponse.match(/Company:\s*(.*)/i)?.[1]?.trim() || "";
    const startDate = aiResponse.match(/Start date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})/i)?.[1] || "";
    const endDate = aiResponse.match(/End date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})/i)?.[1] || "";
    const descriptionMatch = aiResponse.match(/Description:\s*([\s\S]*)/i);
    const parsedDescription = descriptionMatch ? descriptionMatch[1].trim() : "";

    return {
        position,
        company,
        description: parsedDescription,
        startDate,
        endDate,
    } satisfies WorkExperience;
}

export async function generateProjectInfo(input: GenerateProjectInfoInput) {
    const { userId } = await auth();
    if (!userId) {
        throw new Error("User not authenticated");
    }
    const subscriptionLevel = await getPlanDetails();
    if (!canUseAITools(subscriptionLevel)) {
        throw new Error("You need a premium subscription to use AI tools.");
    }
    const { description } = generateProjectInfoSchema.parse(input);
    const systemMessage = `
You are a resume project entry generator AI. Create a project summary from the provided description.

Return the output in this format:

Project Title: <projectTitle>
Project Link: <projectLink>
Start date: <YYYY-MM-DD> (if provided)
End date: <YYYY-MM-DD> (if provided)
Description:
• Point 1
• Point 2
• Point 3

If date is not given, omit it. Do not fabricate fields or include commentary. Keep bullet points achievement-oriented and use clear, professional language.
`;

    const userMessage = `
Based on the following input, generate a project entry:
${description}
`;

    const response = await gemini.models.generateContent({
        model: "gemini-2.0-flash",
        contents: userMessage,
        config: {
            systemInstruction: systemMessage,
        },
    });
    const aiResponse = response.text;
    if (!aiResponse) throw new Error("Failed to generate summary");

    const title = aiResponse.match(/Project Title:\s*(.*)/i)?.[1]?.trim() || "";
    const link = aiResponse.match(/Project Link:\s*(.*)/i)?.[1]?.trim() || "";
    const startDate = aiResponse.match(/Start date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})/i)?.[1] || "";
    const endDate = aiResponse.match(/End date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})/i)?.[1] || "";
    const descriptionMatch = aiResponse.match(/Description:\s*([\s\S]*)/i);
    const parsedDescription = descriptionMatch ? descriptionMatch[1].trim() : "";

    return {
        title,
        link,
        description: parsedDescription,
        startDate,
        endDate,
    } satisfies Project;
}
