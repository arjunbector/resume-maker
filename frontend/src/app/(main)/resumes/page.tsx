import { Metadata } from "next";
import ResumesList from "./ResumesList";
import { useQuery } from "@tanstack/react-query";

export const metadata: Metadata = {
  title: "Resumes",
  description: "Manage your resumes with Resume Maker",
};
export default function ResumesPage() {
    return (
        <div className="container mx-auto p-5">
            <h1 className="text-3xl font-bold text-center">My Resumes</h1>
            <ResumesList/>
        </div>
    )
}
