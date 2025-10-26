import { ResumeValues } from "./validations";

export interface EditorFormProps {
  resumeData: ResumeValues;
  setResumeData: (data: ResumeValues ) => void;
}