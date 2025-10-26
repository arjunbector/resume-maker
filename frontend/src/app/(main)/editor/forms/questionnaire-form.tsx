"use client";

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
import { QuestionAnswerSchema, QuestionAnswerValues } from "@/lib/validations";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm, useFieldArray } from "react-hook-form";
import { toast } from "sonner";

export default function QuestionnaireForm({
  resumeData,
  setResumeData,
}: EditorFormProps) {
  const form = useForm<QuestionAnswerValues>({
    resolver: zodResolver(QuestionAnswerSchema),
    defaultValues: {
      questions: resumeData.questions || [{ ques: "", ans: "" }],
    },
  });

  const { fields } = useFieldArray({
    control: form.control,
    name: "questions",
  });

  const { mutate } = useMutation({
    mutationFn: async (values: QuestionAnswerValues) => {
      console.log(values);
    },
    onSuccess: () => {
      toast.success("Answers saved successfully");
    },
    onError: () => {
      toast.error("Failed to save answers");
    },
  });

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
          className="space-y-5"
          onSubmit={form.handleSubmit((values) => mutate(values))}
        >
          {fields.map((field, index) => (
            <FormField
              key={field.id}
              control={form.control}
              name={`questions.${index}.ans`}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{resumeData.questions?.[index]?.ques}</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Type your answer here..."
                      {...field}
                      rows={3}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          ))}

          <div className="flex justify-end gap-2">
            <Button
              className="cursor-pointer"
              type="reset"
              onClick={() => form.reset()}
              variant="ghost"
              title="This will only reset this page"
            >
              Reset
            </Button>
            <Button type="submit">Save</Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
