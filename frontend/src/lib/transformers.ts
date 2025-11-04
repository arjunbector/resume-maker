import { ResumeValues } from "./validations";

/**
 * Transform backend API response to frontend ResumeValues format
 */
export function transformApiResponseToResumeData(apiResponse: any): ResumeValues {
  console.log("🔍 Raw API Response:", apiResponse);
  
  // Check if response has json wrapper (based on the original format you provided)
  const data = apiResponse.json || apiResponse;
  console.log("🔍 Extracted data:", data);
  
  const { 
    personal_info, 
    professional_profile, 
    target_job, 
    resume_metadata, 
    questionnaire 
  } = data;

  console.log("🔍 Sections:", { personal_info, professional_profile, target_job, resume_metadata, questionnaire });

  const transformedData = {
    // General Info (from resume_metadata)
    title: resume_metadata?.resume_name || "",
    description: resume_metadata?.resume_description || "",

    // Personal Info (from personal_info)
    name: personal_info?.name || "",
    jobTitle: personal_info?.current_job_title || "",
    address: personal_info?.address || "",
    phone: personal_info?.phone || "",
    email: personal_info?.email || "",
    socialMediaHandles: personal_info?.socials || {},

    // Job Description (from target_job)
    applyingJobTitle: target_job?.job_role || "",
    companyName: target_job?.company_name || "",
    companyWebsite: target_job?.company_url || "",
    jobDescriptionString: target_job?.job_description || "",
    jobDescriptionFile: undefined,

    // Questions (from questionnaire)
    questions: questionnaire?.questions?.map((q: any) => ({
      id: q.id,
      ques: q.question,
      ans: q.answer || "",
      relatedField: q.related_field,
      related_field: q.related_field,
      status: q.status || "unanswered",
      // For backwards compatibility with API response
      question: q.question,
      answer: q.answer || "",
    })) || [],

    // Education (from professional_profile.education)
    educations: professional_profile?.education?.map((edu: any) => ({
      degree: edu.degree || "",
      school: edu.institution || "",
      startDate: edu.start_date || "",
      endDate: edu.end_date || "",
      marks: edu.gpa || edu.marks || "",
    })) || [],

    // Projects (from professional_profile.projects)
    projects: professional_profile?.projects?.map((project: any) => ({
      title: project.name || "",
      link: project.url || "",
      startDate: project.start_date || "",
      endDate: project.end_date || "",
      description: project.description || "",
    })) || [],

    // Research Papers (from professional_profile.research_work)
    researchPapers: professional_profile?.research_work?.map((paper: any) => ({
      title: paper.title || "",
      venue: paper.venue || "",
      date: paper.date || "",
      description: paper.description || "",
      url: paper.url || "",
    })) || [],

    // Skills (from professional_profile.skills)
    skills: professional_profile?.skills || [],
  };

  console.log("🔄 Transformed data:", transformedData);
  return transformedData;
}

/**
 * Transform frontend ResumeValues to backend API format
 */
export function transformResumeDataToApiFormat(resumeData: ResumeValues) {
  return {
    personal_info: {
      name: resumeData.name,
      email: resumeData.email,
      phone: resumeData.phone,
      address: resumeData.address,
      current_job_title: resumeData.jobTitle,
      socials: resumeData.socialMediaHandles || {},
    },
    professional_profile: {
      education: resumeData.educations?.map((edu) => ({
        institution: edu.school,
        degree: edu.degree,
        field: "", // You might want to extract this from degree or add a separate field
        start_date: edu.startDate,
        end_date: edu.endDate,
        gpa: edu.marks,
      })) || [],
      projects: resumeData.projects?.map((project) => ({
        name: project.title,
        description: project.description,
        technologies: [], // Empty array for now, could be enhanced later
        url: project.link,
        start_date: project.startDate,
        end_date: project.endDate,
      })) || [],
      research_work: resumeData.researchPapers?.map((paper) => ({
        title: paper.title,
        venue: paper.venue,
        date: paper.date,
        description: paper.description,
        url: paper.url,
      })) || [],
      work_experience: [],
      skills: resumeData.skills || [],
      certifications: [],
      misc: {},
    },
    target_job: {
      job_role: resumeData.applyingJobTitle,
      company_name: resumeData.companyName,
      company_url: resumeData.companyWebsite,
      job_description: resumeData.jobDescriptionString,
      parsed_requirements: [],
      extracted_keywords: [],
    },
    resume_metadata: {
      resume_name: resumeData.title,
      resume_description: resumeData.description,
    },
    questionnaire: {
      questions: resumeData.questions?.map((q: any) => ({
        id: q.id,
        question: q.ques || q.question,
        related_field: q.relatedField || q.related_field,
        answer: q.ans || q.answer,
        status: q.status || "unanswered",
      })) || [],
    },
  };
}
