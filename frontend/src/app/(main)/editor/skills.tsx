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
import { skillsSchema, SkillsValues } from "@/lib/validations";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import SkillsDialog from "./skills-dialog";

// Helper functions to convert between array and comma-separated string
const arrayToCommaSeparated = (arr: string[]): string => {
  return arr.join(", ");
};

const commaSeparatedToArray = (str: string): string[] => {
  return str
    .split(",")
    .map((skill) => skill.trim())
    .filter((skill) => skill.length > 0);
};

export default function SkillsForm({
  resumeData,
  setResumeData,
}: EditorFormProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [showSkills, setShowSkills] = useState<boolean>(false);

  // Use local state to hold the textarea string value
  const [skillsText, setSkillsText] = useState<string>(
    arrayToCommaSeparated(resumeData.skills || [])
  );

  const form = useForm<SkillsValues>({
    resolver: zodResolver(skillsSchema),
    defaultValues: {
      skills: resumeData.skills || [],
    },
  });

  // Update form and parent state when skillsText changes
  useEffect(() => {
    const skillsArray = commaSeparatedToArray(skillsText);
    form.setValue("skills", skillsArray, { shouldValidate: true });

    setResumeData({
      ...resumeData,
      skills: skillsArray,
    });
  }, [skillsText]);

  const { mutate, isPending } = useMutation({
    mutationFn: async (values: SkillsValues) => {
      const payload: SkillsValues = {
        skills:
          values.skills && values.skills.length > 0 ? values.skills : undefined,
      };

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/knowledge-graph/add`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );
      if (!res.ok) {
        throw new Error("Failed to save skills");
      }
    },
    onSuccess: () => {
      toast.success("Skills saved successfully");
      //   const newSearchParams = new URLSearchParams(searchParams);
      //   newSearchParams.set("step", "optimize");
      //   router.push(`/editor?${newSearchParams.toString()}`);
    },
    onError: () => {
      toast.error("Failed to save skills");
    },
  });

  return (
    <>
      {showSkills && <SkillsDialog open={showSkills} setOpen={setShowSkills} />}
      <div className="mx-auto max-w-xl space-y-6">
        <div className="space-y-1.5 text-center">
          <h2 className="text-2xl font-semibold">Skills</h2>
          <p className="text-muted-foreground text-sm">
            Enter your skills separated by commas.
          </p>
        </div>
        <Form {...form}>
          <form
            className="space-y-3"
            onSubmit={form.handleSubmit((values) => mutate(values))}
          >
            <FormField
              control={form.control}
              name="skills"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Skills</FormLabel>
                  <FormControl>
                    <Textarea
                      value={skillsText}
                      onChange={(e) => setSkillsText(e.target.value)}
                      placeholder="Python, JavaScript, React, Node.js, MongoDB"
                      rows={4}
                    />
                  </FormControl>
                  <FormMessage />
                  <p className="text-xs text-muted-foreground mt-2">
                    Separate each skill with a comma. Example: "Python,
                    JavaScript, React"
                  </p>
                </FormItem>
              )}
            />

            <div className="flex justify-end">
              <LoadingButton type="submit" loading={isPending}>
                Next
              </LoadingButton>
            </div>
          </form>
        </Form>
        <div>
          <Button onClick={()=>{
            setShowSkills(true);
          }} className="w-full" variant="outline">
            Show suggested skills
          </Button>
        </div>
      </div>
    </>
  );
}
