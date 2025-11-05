import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z, infer as zodInfer } from "zod";

interface WorkExperienceGenerateDialogProps {
  open: boolean;
  onClose: (open: boolean) => void;
}
export default function WorkExperienceGenerateDialog({
  onClose,
  open,
}: WorkExperienceGenerateDialogProps) {
  const schema = z.object({
    prompt: z
      .string()
      .min(10, "Please provide more details")
      .max(500, "Prompt is too long"),
  });
  type Values = zodInfer<typeof schema>;
  const queryClient = useQueryClient();
  const searchParams = useSearchParams();
  const { mutate, isPending } = useMutation({
    mutationFn: async (data: Values) => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/ai/parse-text`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ text: data.prompt }),
        }
      );
      if (!res.ok) {
        throw new Error("Failed to generate work experience");
      }
    },
    onSuccess: () => {
      const resumeId = searchParams.get("resumeId") || "";
      queryClient.invalidateQueries({ queryKey: ["resumeData", resumeId] });
      onClose(false);
    },
  });
  const form = useForm<Values>();
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate Work Experience</DialogTitle>
        </DialogHeader>
        <div>
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit((values) => mutate(values))}
              className="space-y-4"
            >
              <FormField
                control={form.control}
                name="prompt"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Textarea
                        {...field}
                        placeholder="For example: I worked at Google from March 2022 to March 2025 and I worked on Google Pay."
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="flex justify-end mt-2">
                <LoadingButton loading={isPending}>Generate</LoadingButton>
              </div>
            </form>
          </Form>
        </div>
      </DialogContent>
    </Dialog>
  );
}
