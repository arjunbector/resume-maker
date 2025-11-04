import { email, z } from "zod";

export const optionalString = z.string().trim().optional().or(z.literal(""));

export const authSchema = z.object({
    email: z.string().email(),
    password: z.string().min(6, "Password must be at least 6 characters long"),
})

export type AuthValues = z.infer<typeof authSchema>;

export const genereInfoSchema = z.object({
    title: optionalString,
    description: optionalString,
});

export interface ResumeValues
    extends GeneralInfoValues,
    PersonalInfoValues,
    JobDescriptionValues,
    QuestionAnswerValues,
    EducationValues,
    ProjectsValues,
    SkillsValues,
    ResearchValues,
    WorkExperienceValues { }



export type GeneralInfoValues = z.infer<typeof genereInfoSchema>;

export const personalInfoSchema = z.object({
    name: optionalString,
    jobTitle: optionalString,
    address: optionalString,
    phone: optionalString,
    email: optionalString,
    socialMediaHandles: z.record(z.string(), z.string()).optional(),
});

export type PersonalInfoValues = z.infer<typeof personalInfoSchema>;

export const JobDescriptionSchema = z.object({
    applyingJobTitle: optionalString,
    companyName: optionalString,
    companyWebsite: optionalString,
    jobDescriptionString: optionalString,
    jobDescriptionFile: z.instanceof(File).optional()
})

export type JobDescriptionValues = z.infer<typeof JobDescriptionSchema>;


export const QuestionAnswerSchema = z.object({
    questions: z.array(
        z.object({
            id: z.string().optional(),
            ques: optionalString,
            ans: optionalString,
            relatedField: optionalString,
            related_field: optionalString,
            status: z.enum(["answered", "unanswered"]).optional(),
            // For backwards compatibility with API response
            question: optionalString,
            answer: optionalString,
        })
    )
})
export type QuestionAnswerValues = z.infer<typeof QuestionAnswerSchema>

// Education
export const educationSchema = z.object({
    educations: z
        .array(
            z.object({
                degree: optionalString,
                school: optionalString,
                startDate: optionalString, // ISO date string or empty
                endDate: optionalString,   // ISO date string or empty
                marks: optionalString,
            })
        )
        .optional(),
});

export type EducationValues = z.infer<typeof educationSchema>;

// Projects
export const projectsSchema = z.object({
    projects: z
        .array(
            z.object({
                title: optionalString,
                link: optionalString,
                startDate: optionalString, // ISO date string or empty
                endDate: optionalString,   // ISO date string or empty
                description: optionalString,
            })
        )
        .optional(),
});

export type ProjectsValues = z.infer<typeof projectsSchema>;

// Research
export const researchSchema = z.object({
    researchPapers: z
        .array(
            z.object({
                title: optionalString,
                venue: optionalString,
                date: optionalString, // YYYY-MM or YYYY format
                description: optionalString,
                url: optionalString,
            })
        )
        .optional(),
});

export type ResearchValues = z.infer<typeof researchSchema>;

export const skillsSchema = z.object({
    skills: z
        .array(z.string().trim())
        .optional(),
});
export type SkillsValues = z.infer<typeof skillsSchema>;

// Work Experience
export const workExperienceSchema = z.object({
    workExperiences: z
        .array(
            z.object({
                company: optionalString,
                position: optionalString,
                startDate: optionalString, // ISO date string or empty
                endDate: optionalString,   // ISO date string or empty
                description: optionalString,
            })
        )
        .optional(),
});

export type WorkExperienceValues = z.infer<typeof workExperienceSchema>;