import { Button } from "@/components/ui/button";
import { DownloadCloudIcon } from "lucide-react";

interface PrintResumeButtonProps {
  onPrintClick: () => void;
}
export default function PrintResumeButton({
  onPrintClick,
}: PrintResumeButtonProps) {
  return (
    <Button
      variant="outline"
      size="icon"
      title="Download Resume"
      onClick={() => {
        onPrintClick();
      }}
    >
      <DownloadCloudIcon className="size-4"/>
    </Button>
  );
}