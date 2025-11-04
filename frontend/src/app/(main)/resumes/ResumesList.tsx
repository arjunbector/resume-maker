"use client";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
import { Loader2Icon } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function ResumesList() {
  const router = useRouter();
  const { data, isError, isLoading } = useQuery({
    queryKey: ["resumesList"],
    queryFn: async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/user/all`,
        {
          credentials: "include",
        }
      );
      if (res.ok) {
        const data = await res.json();
        return data.sessions;
      }
    },
  });
  if (isLoading) {
    return (
      <div>
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
      <div className="flex flex-wrap gap-5 mt-10">
        {data.map((res: any) => (
          <ResumeCard resumeId={res.session_id} title={res.resume_name} />
        ))}
      </div>
    </div>
  );
}

interface ResumeCardProps {
  resumeId: string;
  title: string;
}
function ResumeCard({ resumeId, title }: ResumeCardProps) {
  return (
    <Link
      href={`/editor?resumeId=${resumeId}`}
      className="bg-neutral-300 p-5 rounded-2xl"
    >
      <h3>{title}</h3>
    </Link>
  );
}
