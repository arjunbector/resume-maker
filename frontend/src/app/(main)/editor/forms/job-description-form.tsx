import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import LoadingButton from "@/components/ui/loading-button";
import { Textarea } from "@/components/ui/textarea";
import { EditorFormProps } from "@/lib/types";
import { JobDescriptionSchema, JobDescriptionValues } from "@/lib/validations";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import LoadingPopup from "./loading-popup";
import { compareSkills, generateQuestionnaire } from "@/lib/api";
interface JobDescriptionFormProps extends EditorFormProps {
  resumeData: any;
  setResumeData: (resumeData: any) => void;
}
export default function JobDescriptionForm({
  resumeData,
  setResumeData,
}: JobDescriptionFormProps) {
  const form = useForm<JobDescriptionValues>({
    resolver: zodResolver(JobDescriptionSchema),
    defaultValues: {
      applyingJobTitle: resumeData.applyingJobTitle,
      jobDescriptionString: resumeData.jobDescriptionString,
      jobDescriptionFile: resumeData.jobDescriptionFile,
    },
  });
  const router = useRouter();
  const searchparams = useSearchParams();
  const session_id = searchparams.get("resumeId");
  const [showPopup, setShowPopup] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const { isPending, mutate } = useMutation({
    mutationFn: async (values: JobDescriptionValues) => {
      setShowPopup(true);
      setCurrentStep(0);

      // Step 1: Analyze job description
      const analyzeData = {
        job_role: values.applyingJobTitle,
        job_description: values.jobDescriptionString,
        company_name: values.companyName,
        session_id: session_id,
      };

      const analyzeResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/ai/analyze`,
        {
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
          body: JSON.stringify(analyzeData),
          credentials: "include",
        }
      );

      if (!analyzeResponse.ok) {
        console.log("herer");
        throw new Error("Failed to analyze job description");
      }

      const analyzeResult = await analyzeResponse.json();
      setCurrentStep(1);
      // Step 2: Compare skills
      const compareResult = await compareSkills(session_id!);
      setCurrentStep(2);
      let questionnaireResult: any = null;
      if (compareResult.total_missing > 0) {
        // Step 3: Generate questionnaire
        questionnaireResult = await generateQuestionnaire(session_id!);
        setCurrentStep(3);
      } else {
        const newSearchParams = new URLSearchParams(searchparams);
        newSearchParams.set("step", "optimize");
        router.push(`/editor?${newSearchParams.toString()}`);
      }

      return {
        analyze: analyzeResult,
        compare: compareResult,
        questionnaire: questionnaireResult,
      };
    },
    onSuccess: (data) => {
      toast.success("Job description processed successfully");
      setShowPopup(false);
      setCurrentStep(0);

      // Transform and save questionnaire data
      const newSearchParams = new URLSearchParams(searchparams);

      if (
        data.questionnaire?.questions &&
        data.questionnaire?.questions.length > 0
      ) {
        const transformedQuestions = data.questionnaire.questions.map(
          (q: any) => ({
            id: q.id,
            ques: q.question,
            ans: q.answer || "",
            relatedField: q.related_field,
            status: q.status,
          })
        );

        setResumeData({
          ...resumeData,
          questions: transformedQuestions,
        });
        newSearchParams.set("step", "questionnaire");
      } else {
        newSearchParams.set("step", "optimize");
      }


      router.push(`/editor?${newSearchParams.toString()}`);
    },
    onError: (error) => {
      if (error) {
        toast.error(error.message);
      }
      toast.error("Failed to process job description");
      setShowPopup(false);
      setCurrentStep(0);
    },
  });

  // Reset form when resumeData changes
  useEffect(() => {
    form.reset({
      applyingJobTitle: resumeData.applyingJobTitle || "",
      companyName: resumeData.companyName || "",
      companyWebsite: resumeData.companyWebsite || "",
      jobDescriptionString: resumeData.jobDescriptionString || "",
      jobDescriptionFile: resumeData.jobDescriptionFile,
    });
  }, [resumeData.applyingJobTitle, resumeData.companyName, resumeData.companyWebsite, resumeData.jobDescriptionString, resumeData.jobDescriptionFile, form]);

  useEffect(() => {
    const subscription = form.watch((values) => {
      if (form.formState.isValid) {
        setResumeData({
          ...resumeData,
          ...values,
        });
      }
    });

    return () => subscription.unsubscribe();
  }, [form, resumeData, setResumeData]);

  return (
    <>
      <LoadingPopup
        open={showPopup}
        setOpen={setShowPopup}
        currentStep={currentStep}
      />

      <div className="mx-auto max-w-xl space-y-6">
        <div className="space-y-1.5 text-center">
          <h2 className="text-2xl font-semibold">Job Description</h2>
          <p className="text-muted-foreground text-sm">
            Tell us about the job you are applying for.
          </p>
          <Form {...form}>
            <form
              className="space-y-3"
              onSubmit={form.handleSubmit((values) => mutate(values))}
            >
              <FormField
                {...form}
                name="applyingJobTitle"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Job Title</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                {...form}
                name="jobDescriptionString"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Job Description
                      <span className="font-extralight">(optional)</span>
                    </FormLabel>
                    <FormControl>
                      <Textarea {...field} rows={10} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              {/* <FormField
              {...form}
              name="jobDescriptionFile"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Job Description File
                    <span className="font-extralight">(PDF*)</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      type="file"
                      onChange={(e) => field.onChange(e.target.files?.[0])}
                      onBlur={field.onBlur}
                      name={field.name}
                      ref={field.ref}
                    />
                  </FormControl>
                </FormItem>
              )}
            /> */}

              <FormField
                {...form}
                name="companyName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Company Name</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                {...form}
                name="companyWebsite"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Company Website</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="flex justify-end">
                <Button
                  className="cursor-pointer"
                  type="reset"
                  onClick={() => {
                    form.reset();
                  }}
                  variant="ghost"
                  title="This will only reset this page"
                >
                  Reset
                </Button>
                <LoadingButton type="submit" loading={isPending}>
                  Next
                </LoadingButton>
              </div>
            </form>
          </Form>
        </div>
      </div>
    </>
  );
}
