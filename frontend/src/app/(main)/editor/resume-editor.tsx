"use client";

import { cn } from "@/lib/utils";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import ResumePreviewSection from "./resume-preview-section";
import { steps } from "./steps";
import BreadCrumbs from "./bread-crumbs";
import Footer from "./footer";
import { ResumeValues } from "@/lib/validations";
import { useMutation, useQuery } from "@tanstack/react-query";

// interface ResumeEditorProps {
//   resumeToEdit: ResumeServerData | null;
// }

export default function ResumeEditor() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const mutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/new`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      const data = await res.json();
      return data.session_id;
    },
    onSuccess: (data) => {
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set("resumeId", data);
      window.history.pushState(null, "", `?${newSearchParams.toString()}`);
    },
    onError: () => {
      router.push("/");
    },
  });

  const query = useQuery({
    queryKey: ["resumeData", searchParams.get("resumeId")],
    queryFn: async () => {
      const resumeId = searchParams.get("resumeId");
      if (!resumeId) return null;
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/${resumeId}/resume-data`,
        {
          method: "GET",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (!res.ok) {
        throw new Error("Failed to fetch resume data");
      }
      const data = await res.json();
      return data as ResumeValues;
    },
    enabled: !!searchParams.get("resumeId"),
  });

  const [resumeData, setResumeData] = useState<ResumeValues>({
    // General info
    title: "",
    description: "",
    // Personal info (optional at init; will be filled by forms)
    name: "",
    jobTitle: "",
    address: "",
    phone: "",
    email: "",
    socialMediaHandles: {},
    // Job description
    applyingJobTitle: "",
    companyName: "",
    companyWebsite: "",
    jobDescriptionString: "",
    jobDescriptionFile: undefined as unknown as File | undefined,
    // Questionnaire
    questions: [],
  });
  console.log(resumeData);
  const [showSmResumePreview, setShowSmResumePreview] = useState(false);

  const resumeId = searchParams.get("resumeId");
  useEffect(() => {
    // Only create a new session if there's no resumeId in the URL
    if (!resumeId) {
      mutation.mutate();
    }
  }, []); // Empty dependency array to run only once on mount

  const currentStep = searchParams.get("step") || steps[0].key;
  function setStep(key: string) {
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set("step", key);
    window.history.pushState(null, "", `?${newSearchParams.toString()}`);
  }

  const FormComponent = steps.find(
    (step) => step.key === currentStep
  )?.component;

  return (
    <div className="flex h-full grow flex-col">
      <header className="space-y-1.5 border-b px-3 py-5 text-center">
        <h1 className="text-2xl font-bold">Design Resume</h1>
        <p className="text-muted-foreground text-sm">
          Follow the steps below to create your resume, your progress will be
          saved automatically.
        </p>
      </header>
      <main className="relative h-full flex-1 grow">
        <div className="absolute top-0 bottom-0 flex w-full">
          <div
            className={cn(
              "w-full space-y-6 overflow-y-auto p-3 md:block md:w-1/2",
              showSmResumePreview && "hidden"
            )}
          >
            <BreadCrumbs currentStep={currentStep} setCurrentStep={setStep} />
            {FormComponent ? (
              <FormComponent
                resumeData={resumeData}
                setResumeData={setResumeData}
              />
            ) : null}
          </div>
          <div className="grow md:border-r" />
          <ResumePreviewSection
            className={cn(showSmResumePreview && "flex")}
            resumeData={resumeData}
            setResumeData={setResumeData}
          />
        </div>
      </main>
      {/* <Footer
        currentStep={currentStep}
        setCurrentStep={setStep}
        setShowSmResumePreview={setShowSmResumePreview}
        showSmResumePreview={showSmResumePreview}
        isSaving={isSaving}
      /> */}
      <Footer currentStep={currentStep} setCurrentStep={setStep} />
    </div>
  );
}
