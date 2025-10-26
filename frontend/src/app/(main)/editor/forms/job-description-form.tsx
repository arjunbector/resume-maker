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
import { Textarea } from "@/components/ui/textarea";
import { EditorFormProps } from "@/lib/types";
import { JobDescriptionSchema, JobDescriptionValues } from "@/lib/validations";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
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

  const { isPending, mutate } = useMutation({
    mutationFn: async (values: JobDescriptionValues) => {
      const data = {
        job_role: values.applyingJobTitle,
        company_url: values.companyWebsite,
        job_description: values.jobDescriptionString,
      };
      // const data = {
      //   job_role: "Senior Firmware Engineer",
      //   company_url: "https://kshaminnovation.in",
      //   job_description: "We are looking for a senior firmware engineer...",
      // };
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/job-questions`,
        {
          headers: {
            "Content-Type": "application/json",
          },
          method: "POST",
          body: JSON.stringify(data),
        }
      );
      return response.json();
    },
    onSuccess: (data) => {
      toast.success("Job description processed successfully");
      setResumeData({
        ...resumeData,
        questions: data.questions
          ? data.questions.map((q: string) => ({
              ques: q,
              ans: "",
            }))
          : [],
      });
      router.push("/editor?step=questionnaire");
    },
    onError: (error) => {
      toast.error("Failed to process job description");
    },
  });

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
            <FormField
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
            />

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
              <Button
                className="cursor-pointer"
                type="submit"
                variant="default"
                title="This will only reset this page"
                disabled={isPending}
              >
                {isPending ? "Processing..." : "Process"}
              </Button>
            </div>
          </form>
        </Form>
      </div>
    </div>
  );
}
