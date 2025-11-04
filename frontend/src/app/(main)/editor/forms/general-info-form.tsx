import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import LoadingButton from "@/components/ui/loading-button";
import { EditorFormProps } from "@/lib/types";
import { GeneralInfoValues, genereInfoSchema } from "@/lib/validations";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

export default function GeneralInfoForm({
  resumeData,
  setResumeData,
}: EditorFormProps) {
  const form = useForm<GeneralInfoValues>({
    resolver: zodResolver(genereInfoSchema),
    defaultValues: {
      title: resumeData.title || "",
      description: resumeData.description || "",
    },
    mode: "onChange", // Enable validation on change
  });
  const router = useRouter();
  const searchparams = useSearchParams();
  const session_id = searchparams.get("resumeId");
  const { mutate, isPending } = useMutation({
    mutationFn: async (values: GeneralInfoValues) => {
      const data = {
        resume_name: values.title,
        resume_description: values.description,
      };
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions?session_id=${session_id}`,
        {
          method: "PUT",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        }
      );
      if (response.status != 200) {
        throw new Error("Something went wrong");
      }
      return response.json();
    },
    onSuccess: () => {
      toast.success("General info saved successfully");
      const newSearchParams = new URLSearchParams(searchparams);
      newSearchParams.set("step", "personal-info");
      router.push(`/editor?${newSearchParams.toString()}`);
    },
    onError: () => {
      toast.error("Failed to save general info");
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
        <h2 className="text-2xl font-semibold">General info</h2>
        <p className="text-muted-foreground text-sm">
          This will not appear on your resume.
        </p>
      </div>
      <Form {...form}>
        <form
          className="space-y-3"
          onSubmit={form.handleSubmit((values) => mutate(values))}
        >
          <FormField
            control={form.control}
            name="title"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Resume name</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="My cool resume" autoFocus />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Description</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="A resume for my next job" />
                </FormControl>
                <FormDescription>
                  Describe what this resume is for.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="flex justify-end">
            <LoadingButton type="submit" loading={isPending}>
              Next
            </LoadingButton>
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
  );
}
