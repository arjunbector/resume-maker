import { z } from "zod";

export const optionalString = z.string().trim().optional().or(z.literal(""));

export const genereInfoSchema = z.object({
    title: optionalString,
    description: optionalString,
});

export type GeneralInfoValues = z.infer<typeof genereInfoSchema>;

export const personalInfoSchema = z.object({
    firstName: optionalString,
    lastName: optionalString,
    jobTitle: optionalString,
    city: optionalString,
    country: optionalString,
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