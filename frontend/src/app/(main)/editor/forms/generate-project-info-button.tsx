import LoadingButton from "@/components/loading-button";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
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
import { Textarea } from "@/components/ui/textarea";
import {
  GenerateProjectInfoInput,
  GenerateWorkExperienceInput,
  generateWorkExperienceSchema,
  Project,
  WorkExperience,
} from "@/lib/validations";
import { zodResolver } from "@hookform/resolvers/zod";
import { WandSparklesIcon } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { generateProjectInfo, generateWorkExperience } from "./actions";
import { useSubscriptionLevel } from "../../subscription-level-provider";
import usePremiumModal from "@/hooks/usePremiumModal";
import { canUseAITools } from "@/lib/permissions";

interface GenerateProjectInfoButtonProps {
  onProjectGenerated: (project: Project) => void;
}
export default function GenerateProjectInfoButton({
  onProjectGenerated,
}: GenerateProjectInfoButtonProps) {
  const subscriptionLevel = useSubscriptionLevel();
  const { setOpen } = usePremiumModal();
  const [showInputDialog, setShowInputDialog] = useState(false);
  return (
    <>
      <Button
        variant="outline"
        type="button"
        onClick={() => {
          if (!canUseAITools(subscriptionLevel)) {
            setOpen(true);
            return;
          }
          setShowInputDialog(true);
        }}
      >
        <WandSparklesIcon className="size-4" />
        Smart fill (AI)
      </Button>
      <InputDialog
        open={showInputDialog}
        onOpenChange={setShowInputDialog}
        onProjectGenerated={(project) => {
          onProjectGenerated(project);
          setShowInputDialog(false);
        }}
      />
    </>
  );
}

interface InputDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onProjectGenerated: (project: Project) => void;
}

function InputDialog({
  onOpenChange,
  open,
  onProjectGenerated,
}: InputDialogProps) {
  const form = useForm<GenerateProjectInfoInput>({
    resolver: zodResolver(generateWorkExperienceSchema),
    defaultValues: {
      description: "",
    },
  });
  const onSubmit = async (input: GenerateWorkExperienceInput) => {
    try {
      const res = await generateProjectInfo(input);
      onProjectGenerated(res);
    } catch (error) {
      console.error("Error generating project:", error);
      toast.error("Failed to generate project. Please try again.");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate Project Info</DialogTitle>
          <DialogDescription>
            Describe the project and the AI will generate an optimized
            description for you.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-3">
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea
                      {...field}
                      placeholder={`E.g. "Built a fitness tracking website (Jan 2024 - Apr 2024) where users can log in, see their progress, and view charts in real time."`}
                      autoFocus
                      rows={4}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <LoadingButton type="submit" loading={form.formState.isSubmitting}>
              Generate
            </LoadingButton>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
