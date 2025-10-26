import { Button } from "@/components/ui/button";
import { steps } from "./steps";
interface FooterProps {
  currentStep: string;
  setCurrentStep: (step: string) => void;
}
export default function Footer({ currentStep, setCurrentStep }: FooterProps) {
  const prevStep = steps.find(
    (_, idx) => steps[idx + 1]?.key === currentStep
  )?.key;
  const nextStep = steps.find(
    (_, idx) => steps[idx - 1]?.key === currentStep
  )?.key;
  return (
    <footer className="w-full border-t bg-background/50 text-center p-4 text-sm flex justify-end">
      <p className="text-muted-foreground">
        <Button
          onClick={() => {
            if (nextStep) {
              setCurrentStep(nextStep);
            }
          }}
          disabled={!nextStep}
        >
          Next
        </Button>
      </p>
    </footer>
  );
}
