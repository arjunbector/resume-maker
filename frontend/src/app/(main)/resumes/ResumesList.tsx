"use client";
import { Button } from "@/components/ui/button";
import { useQuery } from "@tanstack/react-query";
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

  if (data?.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center my-6">
        <Button onClick={()=>{
            router.push("/editor")
        }}>New Resume</Button>
      </div>
    );
  }
  return <div></div>;
}
