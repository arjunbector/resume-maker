// import { EditorFormProps } from "@/lib/types";
import React from "react";
import EducationalForm from "./forms/educational-form";
import GeneralInfoForm from "./forms/general-info-form";
import PersonalInfoForm from "./forms/personal-info-form";
import SkillsForm from "./forms/skills-form";
import WorkExperienceForm from "./forms/work-experience-form";
import SummaryForm from "./forms/summary-form";
import ProjectsForm from "./forms/projects-form";
import { EditorFormProps } from "@/lib/types";
import JobDescriptionForm from "./forms/job-description-form";

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
  //   {
  //     title: "Work Experience",
  //     component: WorkExperienceForm,
  //     key: "work-experience",
  //   },
  //   {
  //     title: "Education",
  //     component: EducationalForm,
  //     key: "education",
  //   },
  //   {
  //     title: "Projects",
  //     component: ProjectsForm,
  //     key: "projects",
  //   },
  //   {
  //     title: "Skills",
  //     component: SkillsForm,
  //     key: "skills",
  //   },
  //   {
  //     title: "Summary",
  //     component: SummaryForm,
  //     key: "summary",
  //   },
];
