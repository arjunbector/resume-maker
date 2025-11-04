import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { TextShimmer } from "@/components/ui/text-shimmer";
import { CheckIcon, Loader2Icon } from "lucide-react";

interface LoadingPopupProps {
  open: boolean;
  setOpen: (open: boolean) => void;
  currentStep: number;
}

const STEPS = [
  {
    label: "Analyzing your job description",
  },
  {
    label: "Comparing your skills with the job requirements",
  },
  {
    label: "Generating questions",
  },
];

export default function LoadingPopup({
  open,
  setOpen,
  currentStep,
}: LoadingPopupProps) {
  return (
    <Dialog open={open}>
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>Processing your resume...</DialogTitle>
        </DialogHeader>
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
              <span
                className={index < currentStep ? "text-muted-foreground" : ""}
              >
                {index === currentStep ? (
                  <TextShimmer>{step.label}</TextShimmer>
                ) : (
                  step.label
                )}
              </span>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
