"use client";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { EditorFormProps } from "@/lib/types";
import { QuestionAnswerSchema, QuestionAnswerValues } from "@/lib/validations";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm, useFieldArray } from "react-hook-form";
import { toast } from "sonner";
import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { compareSkills, generateQuestionnaire } from "@/lib/api";
import LoadingButton from "@/components/ui/loading-button";

export default function QuestionnaireForm({
  resumeData,
  setResumeData,
}: EditorFormProps) {
  const searchParams = useSearchParams();
  const session_id = searchParams.get("resumeId");

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

  // Update form when resumeData.questions changes
  useEffect(() => {
    if (resumeData.questions && resumeData.questions.length > 0) {
      form.reset({
        questions: resumeData.questions.map((q: any) => ({
          ques: q.ques || q.question || "",
          ans: q.ans || q.answer || "",
        })),
      });
    }
  }, [resumeData.questions, form]);
  const router = useRouter();

  const { mutate, isPending } = useMutation({
    mutationFn: async (values: QuestionAnswerValues) => {
      if (!session_id) {
        throw new Error("Session ID is required");
      }

      // Build answers object with question IDs as keys
      const answers: Record<string, string> = {};
      resumeData.questions?.forEach((q: any, index: number) => {
        const answer = values.questions[index]?.ans || "";
        const questionId = q.id;
        if (questionId && answer.trim()) {
          answers[questionId] = answer.trim();
        }
      });

      // Prepare payload
      const payload = {
        session_id: session_id,
        answers: answers,
      };

      // Call API to save answers
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/ai/answer-question`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
          credentials: "include",
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || "Failed to save answers");
      }

      const responseData = await response.json();

      // Update resumeData with answers
      const updatedQuestions =
        resumeData.questions?.map((q: any, index: number) => ({
          ...q,
          ans: values.questions[index]?.ans || "",
          answer: values.questions[index]?.ans || "",
          status: values.questions[index]?.ans ? "answered" : "unanswered",
        })) || [];

      let updatedResumeData = {
        ...resumeData,
        questions: updatedQuestions,
      };

      // After saving answers, check if we need to generate more questions
      if (response.ok) {
        const compareResult = await compareSkills(session_id);

        if (compareResult?.total_missing && compareResult.total_missing !== 0) {
          console.log(compareResult);
          // Generate new questions if there are missing skills
          const questionnaireResult = await generateQuestionnaire(session_id);

          // Transform and update resumeData with new questions
          if (questionnaireResult?.questions) {
            const transformedQuestions = questionnaireResult.questions.map(
              (q: any) => ({
                id: q.id,
                ques: q.question,
                ans: q.answer || "",
                relatedField: q.related_field,
                status: q.status,
              })
            );

            updatedResumeData = {
              ...updatedResumeData,
              questions: transformedQuestions,
            };
          }
        } else {
          const newSearchParams = new URLSearchParams(searchParams);
          newSearchParams.set("step", "optimize");
          router.push(`/editor?${newSearchParams.toString()}`);
        }
      }

      // Update resumeData once with all changes
      setResumeData(updatedResumeData);

      return responseData;
    },
    onSuccess: () => {
      toast.success("Answers saved successfully");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to save answers");
    },
  });

  if (!resumeData.questions || resumeData.questions.length === 0) {
    return (
      <div className="mx-auto max-w-xl space-y-6">
        <div className="space-y-1.5 text-center">
          <h2 className="text-2xl font-semibold">Questionnaire</h2>
          <p className="text-muted-foreground text-sm">
            No questions available. Please complete the job description step
            first.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div className="space-y-1.5 text-center">
        <h2 className="text-2xl font-semibold">Questionnaire</h2>
        <p className="text-muted-foreground text-sm">
          Answer the following questions to help us tailor your resume.
        </p>
      </div>

      <Form {...form}>
        <form
          className="space-y-6"
          onSubmit={form.handleSubmit((values) => mutate(values))}
        >
          {fields.map((field, index) => {
            const question = resumeData.questions?.[index];
            const relatedField =
              (question as any)?.relatedField ||
              (question as any)?.related_field;

            return (
              <Card key={field.id}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <FormLabel className="text-base font-semibold leading-tight">
                      {question?.ques ||
                        question?.question ||
                        `Question ${index + 1}`}
                    </FormLabel>
                    {relatedField && (
                      <Badge variant="secondary" className="shrink-0">
                        {relatedField}
                      </Badge>
                    )}
                  </div>
                  {/* {relatedField && (
                    <FormDescription className="text-xs">
                      Related to: {relatedField}
                    </FormDescription>
                  )} */}
                </CardHeader>
                <CardContent>
                  <FormField
                    control={form.control}
                    name={`questions.${index}.ans`}
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <Textarea
                            placeholder="Type your answer here..."
                            {...field}
                            rows={4}
                            className="resize-none"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </CardContent>
              </Card>
            );
          })}

          <div className="flex justify-end gap-2 pt-4">
            <Button
              className="cursor-pointer"
              type="reset"
              onClick={() => form.reset()}
              variant="ghost"
              title="This will only reset this page"
              disabled={isPending}
            >
              Reset
            </Button>
            <LoadingButton type="submit" loading={isPending}>
              Save
            </LoadingButton>
          </div>
        </form>
      </Form>
    </div>
  );
}
