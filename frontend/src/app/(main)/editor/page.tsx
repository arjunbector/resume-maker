import { Metadata } from "next";
import ResumeEditor from "./resume-editor";

interface PageProps {
  searchParams: Promise<{ resumeId?: string }>;
}

export const metadata: Metadata = {
  title: "Resume Editor",
};

export default async function EditorPage({ searchParams }: PageProps) {
  return (
    <div className="flex h-full grow flex-col container mx-auto">
      <ResumeEditor />
    </div>
  );
}
