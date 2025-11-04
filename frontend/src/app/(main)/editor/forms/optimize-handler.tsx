"use client";

import { useQuery } from "@tanstack/react-query";
import { CheckIcon, Loader2Icon } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function OptimizeHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const query = useQuery({
    queryKey: ["optimize"],
    queryFn: async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/ai/optimize`,
        {
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
          credentials: "include",
        }
      );
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.message || "Failed to optimize");
      }
      return res.json();
    },
  });
  if (query.data) {
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set("step", "education");
    router.push(`/editor?${newSearchParams.toString()}`);
  }
  const STEPS = [
    { label: "Optimizing resume content" },
    { label: "Improving keyword coverage for ATS" },
    { label: "Tailoring achievements to the role" },
    { label: "Applying formatting and readability tweaks" },
    { label: "Finalizing personalized suggestions" },
  ];

  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    // Simulate backend progress; replace with real progress updates if available
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 900);
    if (query.isSuccess || query.isError) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [query.isSuccess, query.isError]);

  return (
    <div className="space-y-4">
      {STEPS.map((step, index) => (
        <div key={step.label} className="flex items-center gap-2">
          {index < currentStep ? (
            <CheckIcon className="size-4 text-green-600" />
          ) : index === currentStep ? (
            <Loader2Icon className="size-4 animate-spin" />
          ) : (
            <div className="size-4" />
          )}
          <span className={index < currentStep ? "text-muted-foreground" : ""}>
            {step.label}
          </span>
        </div>
      ))}
    </div>
  );
}
