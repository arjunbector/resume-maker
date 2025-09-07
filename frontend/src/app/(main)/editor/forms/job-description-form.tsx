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
import { useEffect } from "react";
import { useForm } from "react-hook-form";
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
        <p className="text-muted-foreground text-sm">Tell us about the job you are applying for.</p>
        <Form {...form}>
          <form className="space-y-3">
            <div className="grid grid-cols-1 gap-3">
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
                    <FormLabel>Job Description<span className="font-extralight">(optional)</span></FormLabel>
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
                    <FormLabel>Job Description File<span className="font-extralight">(PDF*)</span></FormLabel>
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
            </div>

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
            </div>
          </form>
        </Form>
      </div>
    </div>
  );
}
