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
    QuestionAnswerValues { }



export type GeneralInfoValues = z.infer<typeof genereInfoSchema>;

export const personalInfoSchema = z.object({
    name: optionalString,
    jobTitle: optionalString,
    address: optionalString,
    phone: optionalString,
    email: optionalString,
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
            ques: optionalString,
            ans: optionalString
        })
    )
})
export type QuestionAnswerValues = z.infer<typeof QuestionAnswerSchema>