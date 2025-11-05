import { EditorFormProps } from "@/lib/types";
import React from "react";
import EducationalForm from "./education-form";
import GeneralInfoForm from "./forms/general-info-form";
import JobDescriptionForm from "./forms/job-description-form";
import Optimize from "./forms/optimize";
import PersonalInfoForm from "./forms/personal-info-form";
import QuestionnaireForm from "./forms/questionnaire-form";
import ProjectsForm from "./projects-form";
import SkillsForm from "./skills";
import WorkExperienceForm from "./forms/work-experience-form";
import ResearchForm from "./research-form";

export const steps: {
  title: string;
  component: React.ComponentType<EditorFormProps>;
  key: string;
}[] = [
  {
    title: "General Info",
    component: GeneralInfoForm,
    key: "general-info",
  },
  {
    title: "Personal Info",
    component: PersonalInfoForm,
    key: "personal-info",
  },
  {
    title: "Job Description",
    component: JobDescriptionForm,
    key: "job-description",
  },
  {
    title: "Questionnaire",
    component: QuestionnaireForm,
    key: "questionnaire",
  },
  {
    title: "Optimize",
    component: Optimize,
    key: "optimize",
  },
  {
    title: "Work Experience",
    component: WorkExperienceForm,
    key: "work-experience",
  },
  {
    title: "Education",
    component: EducationalForm,
    key: "education",
  },
  {
    title: "Projects",
    component: ProjectsForm,
    key: "projects",
  },
  {
    title: "Research Work",
    component: ResearchForm,
    key: "research-work",
  },
  {
    title: "Skills",
    component: SkillsForm,
    key: "skills",
  },
  //   {
  //     title: "Summary",
  //     component: SummaryForm,
  //     key: "summary",
  //   },
];
