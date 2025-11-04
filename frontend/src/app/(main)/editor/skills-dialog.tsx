import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { AlertCircle, Lightbulb, Loader2Icon } from "lucide-react";
import { TextShimmer } from "@/components/ui/text-shimmer";

interface Suggestion {
  field_name: string;
  suggestion: string;
  category: string;
}

interface SkillsDialogProps {
  open: boolean;
  setOpen: (open: boolean) => void;
}
export default function SkillsDialog({ open, setOpen }: SkillsDialogProps) {
  const searchParams = useSearchParams();
  const query = useQuery({
    queryKey: ["recommended skills", searchParams.get("resumeId")],
    queryFn: async () => {
      const res = await fetch(
        `${
          process.env.NEXT_PUBLIC_API_URL
        }/api/v1/ai/compare?session_id=${searchParams.get("resumeId")}`,
        {
            method:"POST",
            credentials:"include",
        }
      );
      if (res.ok) {
        const data = await res.json();
        return data.fill_suggestions as Suggestion[]; // Assuming the response has a json field containing the array
      }
      throw new Error('Failed to fetch suggestions');
    },
  });

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'experience':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'skills':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'education':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'projects':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            AI Resume Recommendations
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-blue-800">
              Based on the job requirements, here are personalized suggestions to strengthen your resume and improve your chances of landing this role.
            </p>
          </div>

          <div className="space-y-3">
            {query.isLoading && (
              <div className="flex items-center justify-center py-8">
                <Loader2Icon className="size-6 animate-spin text-neutral-500"/>
                <span className="ml-2 text-muted-foreground"><TextShimmer>Analyzing your resume...</TextShimmer></span>
              </div>
            )}
            
            {query.isError && (
              <Card className="border-red-200 bg-red-50">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-2 text-red-700">
                    <AlertCircle className="w-4 h-4" />
                    <span>Failed to load recommendations. Please try again later.</span>
                  </div>
                </CardContent>
              </Card>
            )}
            
            {query.data && query.data.length > 0 && (
              <div className="space-y-3">
                {query.data.map((suggestion, index) => (
                  <Card key={index} className="border-l-4 border-l-primary">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg font-medium text-primary">
                          {suggestion.field_name}
                        </CardTitle>
                        <Badge 
                          variant="outline" 
                          className={getCategoryColor(suggestion.category)}
                        >
                          {suggestion.category.charAt(0).toUpperCase() + suggestion.category.slice(1)}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="text-sm leading-relaxed">
                        {suggestion.suggestion}
                      </CardDescription>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
            
            {query.data && query.data.length === 0 && (
              <Card className="border-green-200 bg-green-50">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <Lightbulb className="w-12 h-12 text-green-600 mx-auto mb-2" />
                    <h3 className="font-medium text-green-800 mb-1">Great job!</h3>
                    <p className="text-sm text-green-700">
                      Your resume looks well-aligned with the job requirements. No specific improvements needed at this time.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
