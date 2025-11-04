import { cn } from "@/lib/utils";
import { Loader2Icon } from "lucide-react";
import { Button } from "./button";

interface LoadingButtonProps extends React.ComponentProps<"button"> {
  loading: boolean;
  className?: string;
  children: React.ReactNode;
}
export default function LoadingButton({
  loading,
  className,
  children,
  ...props
}: LoadingButtonProps) {
  return (
    <Button className={cn(className)} disabled={loading}>
      {loading && <Loader2Icon className="animate-spin size-4" />}
      {children}
    </Button>
  );
}
