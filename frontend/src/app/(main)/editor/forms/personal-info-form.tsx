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
import { EditorFormProps } from "@/lib/types";
import { personalInfoSchema, PersonalInfoValues } from "@/lib/validations";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

// Function to parse URL and extract platform name
function parseSocialMediaUrl(
  url: string
): { platform: string; url: string } | null {
  if (!url || url.trim() === "") return null;

  // Normalize URL (add https:// if missing)
  let normalizedUrl = url.trim();
  if (!normalizedUrl.match(/^https?:\/\//i)) {
    normalizedUrl = `https://${normalizedUrl}`;
  }

  try {
    const urlObj = new URL(normalizedUrl);
    const hostname = urlObj.hostname.toLowerCase();

    // Remove www. prefix if present
    const cleanHostname = hostname.replace(/^www\./, "");

    // Extract platform name from common social media domains
    const platformMap: Record<string, string> = {
      "instagram.com": "instagram",
      "linkedin.com": "linkedin",
      "twitter.com": "twitter",
      "x.com": "twitter",
      "github.com": "github",
      "facebook.com": "facebook",
      "youtube.com": "youtube",
      "tiktok.com": "tiktok",
      "pinterest.com": "pinterest",
      "snapchat.com": "snapchat",
      "reddit.com": "reddit",
      "medium.com": "medium",
      "behance.net": "behance",
      "dribbble.com": "dribbble",
      portfolio: "portfolio",
    };

    // Try to match domain
    for (const [domain, platform] of Object.entries(platformMap)) {
      if (cleanHostname.includes(domain)) {
        return {
          platform,
          url: normalizedUrl.replace(/^https?:\/\//, ""), // Remove protocol
        };
      }
    }

    // If no match, use the domain name as platform
    const domainParts = cleanHostname.split(".");
    const platform =
      domainParts.length > 1
        ? domainParts[domainParts.length - 2]
        : cleanHostname;

    return {
      platform,
      url: normalizedUrl.replace(/^https?:\/\//, ""),
    };
  } catch {
    // If URL parsing fails, treat the whole string as a custom platform
    return {
      platform: "custom",
      url: normalizedUrl.replace(/^https?:\/\//, ""),
    };
  }
}

export default function PersonalInfoForm({
  resumeData,
  setResumeData,
}: EditorFormProps) {
  const [socialMediaInput, setSocialMediaInput] = useState("");

  const form = useForm<PersonalInfoValues>({
    resolver: zodResolver(personalInfoSchema),
    defaultValues: {
      name: resumeData.name || "",
      jobTitle: resumeData.jobTitle || "",
      address: resumeData.address || "",
      phone: resumeData.phone || "",
      email: resumeData.email || "",
      socialMediaHandles: resumeData.socialMediaHandles || {},
    },
  });
  const router = useRouter();

  const socialMediaHandles = form.watch("socialMediaHandles") || {};

  const addSocialMedia = () => {
    if (!socialMediaInput.trim()) return;

    const parsed = parseSocialMediaUrl(socialMediaInput);
    if (!parsed) {
      toast.error("Invalid URL");
      return;
    }

    const currentHandles = form.getValues("socialMediaHandles") || {};
    form.setValue("socialMediaHandles", {
      ...currentHandles,
      [parsed.platform]: parsed.url,
    });

    setSocialMediaInput("");
  };

  const removeSocialMedia = (platform: string) => {
    const currentHandles = form.getValues("socialMediaHandles") || {};
    const updated = { ...currentHandles };
    delete updated[platform];
    form.setValue("socialMediaHandles", updated);
  };
  const searchParams = useSearchParams();

  const { mutate, isPending } = useMutation({
    mutationFn: async (values: PersonalInfoValues) => {
      const data = {
        name: values.name,
        current_job_title: values.jobTitle,
        address: values.address,
        phone: values.phone,
        resume_email: values.email,
        socials: values.socialMediaHandles,
      };
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/users`,
        {
          method: "PUT",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        }
      );
    },
    onSuccess: () => {
      toast.success("Personal info saved successfully");
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set("step", "job-description");
      router.push(`/editor?${newSearchParams.toString()}`);
    },
    onError: () => {
      toast.error("Failed to save personal info");
    },
  });

  // Reset form when resumeData changes
  useEffect(() => {
    form.reset({
      name: resumeData.name || "",
      jobTitle: resumeData.jobTitle || "",
      address: resumeData.address || "",
      phone: resumeData.phone || "",
      email: resumeData.email || "",
      socialMediaHandles: resumeData.socialMediaHandles || {},
    });
  }, [resumeData.name, resumeData.jobTitle, resumeData.address, resumeData.phone, resumeData.email, resumeData.socialMediaHandles, form]);

  useEffect(() => {
    const subscription = form.watch((values) => {
      if (form.formState.isValid) {
        const handles = values.socialMediaHandles || {};
        // Filter out any undefined values
        const cleanHandles: Record<string, string> = {};
        Object.entries(handles).forEach(([key, value]) => {
          if (value) {
            cleanHandles[key] = value;
          }
        });
        setResumeData({
          ...resumeData,
          ...values,
          socialMediaHandles: cleanHandles,
        });
      }
    });

    return () => subscription.unsubscribe();
  }, [form, resumeData, setResumeData]);

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div className="space-y-1.5 text-center">
        <h2 className="text-2xl font-semibold">Personal Info</h2>
        <p className="text-muted-foreground text-sm">Tell us about yourself.</p>
        <Form {...form}>
          <form
            className="space-y-3"
            onSubmit={form.handleSubmit((values) => mutate(values))}
          >
            <div className="grid grid-cols-2 gap-3">
              <FormField
                {...form}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                {...form}
                name="jobTitle"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Job Title</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              {...form}
              name="address"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Address</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              {...form}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Phone</FormLabel>
                  <FormControl>
                    <Input {...field} type="tel" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              {...form}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input {...field} type="email" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="space-y-3">
              <FormLabel>Social Media Handles (Optional)</FormLabel>
              <div className="flex gap-2">
                <Input
                  placeholder="Paste URL (e.g., instagram.com/username)"
                  value={socialMediaInput}
                  onChange={(e) => setSocialMediaInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      addSocialMedia();
                    }
                  }}
                />
                <Button
                  type="button"
                  onClick={addSocialMedia}
                  variant="outline"
                >
                  Add
                </Button>
              </div>

              {Object.keys(socialMediaHandles).length > 0 && (
                <div className="space-y-2">
                  {Object.entries(socialMediaHandles).map(([platform, url]) => (
                    <div
                      key={platform}
                      className="flex items-center justify-between rounded-md border p-2"
                    >
                      <div className="flex-1">
                        <span className="font-medium capitalize">
                          {platform}:
                        </span>{" "}
                        <span className="text-sm text-muted-foreground">
                          {url}
                        </span>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeSocialMedia(platform)}
                        className="text-destructive hover:text-destructive"
                      >
                        Remove
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-end">
              <LoadingButton type="submit" loading={isPending}>
                Next
              </LoadingButton>
              <Button
                className="cursor-pointer"
                type="reset"
                onClick={() => {
                  form.reset();
                }}
                variant="ghost"
                title="This will only reset this page"
              >
                Reset
              </Button>
            </div>
          </form>
        </Form>
      </div>
    </div>
  );
}
