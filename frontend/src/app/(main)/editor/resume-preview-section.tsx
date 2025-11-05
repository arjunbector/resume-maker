import ResumePreview from "@/components/resume-preview";
import { cn } from "@/lib/utils";
import { useRef } from "react";
import { useReactToPrint } from "react-to-print";
import PrintResumeButton from "./print-resume-button";
import { Button } from "@/components/ui/button";
import { RotateCcw } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";

interface ResumePreviewSectionProps {
  resumeData: any;
  setResumeData: (resumeData: any) => void;
  className?: string;
}
export default function ResumePreviewSection({
  resumeData,
  setResumeData,
  className,
}: ResumePreviewSectionProps) {
  const contentRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  const reactToPrintFn = useReactToPrint({
    contentRef,
    documentTitle: resumeData.title || "Resume",
  });

  const handleRefreshResume = () => {
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set("step", "general-info");
    router.push(`/editor?${newSearchParams.toString()}`);
    window.location.reload();
  };

  return (
    <div
      className={cn("group relative hidden w-full md:flex md:w-1/2", className)}
    >
      <div className="absolute top-1 left-1 flex flex-none flex-col gap-3 opacity-10 transition-opacity group-hover:opacity-100 lg:pt-3 lg:pl-3 2xl:opacity-100">
        {/* <ColorPicker
          color={resumeData.colorHex}
          onChange={(color) => {
            setResumeData({
              ...resumeData,
              colorHex: color.hex,
            });
          }}
        />
        <BorderStyleButton
          borderStyle={resumeData.borderStyle}
          onChange={(newBorderStyle) => {
            setResumeData({
              ...resumeData,
              borderStyle: newBorderStyle,
            });
          }}
        /> */}{" "}
        <PrintResumeButton onPrintClick={reactToPrintFn} />
        <Button
          title="Refresh Resume"
          variant="outline"
          size="icon"
          onClick={handleRefreshResume}
        >
          <RotateCcw />
        </Button>
      </div>
      <div className="bg-secondary flex w-full justify-center overflow-y-auto p-3">
        <ResumePreview
          className="max-w-2xl shadow-md"
          resumeData={resumeData}
          contentRef={contentRef}
        />
      </div>
    </div>
  );
}
