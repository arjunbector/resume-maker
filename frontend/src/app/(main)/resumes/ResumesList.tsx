"use client";
import ResumePreview from "@/components/resume-preview";
import { Button } from "@/components/ui/button";
import { transformApiResponseToResumeData } from "@/lib/transformers";
import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { Loader2Icon } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef } from "react";
import { useReactToPrint } from "react-to-print";

export default function ResumesList() {
  const router = useRouter();
  const { data, isError, isLoading } = useQuery({
    queryKey: ["resumesList"],
    queryFn: async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/user/all/resume-data`,
        {
          credentials: "include",
        }
      );
      if (res.ok) {
        const data = await res.json();
        return data.resume_data;
      }
    },
  });
  if (isLoading) {
    return (
      <div className="mx-auto flex items-center justify-center w-full">
        <Loader2Icon className="size-5 animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center my-6">
      <Button
        onClick={() => {
          router.push("/editor");
        }}
      >
        New Resume
      </Button>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-10">
        {data.length === 0 ? (
          <div>No resumes found.</div>
        ) : (
          data.map((res: any) => (
            <ResumeCard
              key={res.session_id}
              resumeId={res.session_id}
              title={res.resume_metadata.resume_name}
              description={res.resume_metadata.resume_description}
              resume={res}
            />
          ))
        )}
      </div>
    </div>
  );
}

interface ResumeCardProps {
  resumeId: string;
  title: string;
  description?: string;
  resume: any;
}
function ResumeCard({ resumeId, title, description, resume }: ResumeCardProps) {
  const contentRef = useRef<HTMLDivElement>(null);
  const reactToPrintFn = useReactToPrint({
    contentRef,
    documentTitle: title || "Resume",
  });
  console.log("\\n\n\n\n\n\n\n\n\n\n\n\nin card:;", resume);
  // console.log(
  //   "\\n\n\n\n\n\n\n\n\n\n\n\nin card:;",
  //   transformApiResponseToResumeData(resume)
  // );
  return (
    <div className="group hover:border-border bg-secondary relative rounded-lg border border-transparent p-3 transition-colors w-80">
      <div className="space-y-3">
        <Link
          href={`/editor?resumeId=${resumeId}`}
          className="inline-block w-full text-center"
        >
          <p className="line-clamp-1 font-semibold">
            {title || "Untitled Resume"}
          </p>
          {description && <p className="line-clamp-2 text-sm">{description}</p>}
        </Link>
        <Link
          href={`/editor?resumeId=${resumeId}`}
          className="relative inline-block w-full"
        >
          <ResumePreview
            contentRef={contentRef}
            resumeData={transformApiResponseToResumeData(resume)}
            className="overflow-hidden shadow-sm transition-shadow group-hover:shadow-lg"
          />
          <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-white to-transparent" />
        </Link>
        {/* <div className="text-xs text-muted-foreground">
          Last edited {formatDistanceToNow(new Date(resume.resume_metadata.last_active), { addSuffix: true })}
        </div> */}
      </div>
    </div>
  );
}
