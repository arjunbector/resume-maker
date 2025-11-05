import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { EditorFormProps } from "@/lib/types";
import { workExperienceSchema, WorkExperienceValues } from "@/lib/validations";
import { zodResolver } from "@hookform/resolvers/zod";
import { GripHorizontalIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { useFieldArray, useForm, UseFormReturn } from "react-hook-form";
import {
  closestCenter,
  DndContext,
  DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { restrictToVerticalAxis } from "@dnd-kit/modifiers";
import { CSS } from "@dnd-kit/utilities";
import { cn } from "@/lib/utils";
import LoadingButton from "@/components/ui/loading-button";
import { useMutation } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import WorkExperienceGenerateDialog from "./work-experience-generate-dialog";

export default function WorkExperienceForm({
  resumeData,
  setResumeData,
}: EditorFormProps) {
  const form = useForm<WorkExperienceValues>({
    resolver: zodResolver(workExperienceSchema),
    defaultValues: {
      workExperiences: resumeData.workExperiences || [],
    },
  });
  // Fixed useEffect for Work Experiences Form
  useEffect(() => {
    // Create a subscription to watch form changes
    const subscription = form.watch((values) => {
      const { isValid } = form.formState;

      // Only update parent state when form is valid
      if (isValid && values) {
        setResumeData({
          ...resumeData,
          ...values,
          workExperiences: values.workExperiences?.filter(
            (experience): experience is NonNullable<typeof experience> =>
              experience !== undefined
          ),
        });
      }
    });

    // Clean up subscription on unmount
    return () => subscription.unsubscribe();
  }, [form, resumeData, setResumeData]);

  const { fields, append, remove, move } = useFieldArray({
    control: form.control,
    name: "workExperiences",
  });

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id != over.id) {
      const oldIndex = fields.findIndex((field) => field.id === active.id);
      const newIndex = fields.findIndex((field) => field.id === over.id);
      move(oldIndex, newIndex);
      return arrayMove(fields, oldIndex, newIndex);
    }
  };
  const searchParams = useSearchParams();
  const router = useRouter();
  const { mutate, isPending } = useMutation({
    mutationFn: async (data: WorkExperienceValues) => {
      const payload = {
        work_experience:
          data.workExperiences?.map((exp) => ({
            company: exp.company,
            position: exp.position,
            start_date: exp.startDate,
            end_date: exp.endDate,
            description: exp.description,
          })) || [],
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
        throw new Error(`Failed to save work experience: ${res.statusText}`);
      }

      return res.json();
    },
    onSuccess: () => {
      toast.success("Work experiences saved successfully");
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set("step", "education");
      router.push(`/editor?${newSearchParams.toString()}`);
    },
    onError: () => {
      toast.error("Something went wrong.");
    },
  });
  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div className="space-y-1.5 text-center">
        <h2 className="text-2xl font-semibold">Work Experience</h2>
        <p className="text-muted-foreground text-sm">
          Add your work experiences
        </p>
      </div>
      <Form {...form}>
        <form
          className="space-y-3"
          onSubmit={form.handleSubmit((data) => mutate(data))}
        >
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
            modifiers={[restrictToVerticalAxis]}
          >
            <SortableContext
              items={fields}
              strategy={verticalListSortingStrategy}
            >
              {fields.map((field, idx) => (
                <WorkExperienceItem
                  id={field.id}
                  key={field.id}
                  form={form}
                  index={idx}
                  remove={remove}
                />
              ))}
            </SortableContext>
          </DndContext>
          <div className="flex justify-center">
            <Button
              type="button"
              onClick={() => {
                append({
                  company: "",
                  position: "",
                  startDate: "",
                  endDate: "",
                  description: "",
                });
              }}
            >
              Add work experience
            </Button>
          </div>
          <div className="flex justify-end">
            <LoadingButton type="submit" loading={isPending}>
              Next
            </LoadingButton>
          </div>
        </form>
      </Form>
    </div>
  );
}

interface WorkExperienceItemProps {
  form: UseFormReturn<WorkExperienceValues>;
  index: number;
  id: string;
  remove: (index: number) => void;
}
function WorkExperienceItem({
  form,
  index,
  remove,
  id,
}: WorkExperienceItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });
  const [open, setOpen] = useState(false);
  return (
    <>
      <WorkExperienceGenerateDialog onClose={setOpen} open={open} />
      <div
        className={cn(
          "bg-background space-y-3 rounded-md border p-3",
          isDragging && "relative z-100 cursor-grab shadow-xl"
        )}
        ref={setNodeRef}
        style={{ transform: CSS.Transform.toString(transform), transition }}
      >
        <div className="flex justify-between gap-2">
          <span className="font-semibold">Work Experience {index + 1}</span>
          <GripHorizontalIcon
            className="text-muted-foreground size-5 cursor-grab focus:outline-none"
            {...attributes}
            {...listeners}
          />
        </div>

        <FormField
          control={form.control}
          name={`workExperiences.${index}.position`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Job Title</FormLabel>
              <FormControl>
                <Input {...field} autoFocus />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name={`workExperiences.${index}.company`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Company Name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="grid grid-cols-2 gap-3">
          <FormField
            control={form.control}
            name={`workExperiences.${index}.startDate`}
            render={({ field }) => (
              <FormItem>
                <FormLabel>Start Date</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="date"
                    value={field.value?.slice(0, 10)}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name={`workExperiences.${index}.endDate`}
            render={({ field }) => (
              <FormItem>
                <FormLabel>End Date</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="date"
                    value={field.value?.slice(0, 10)}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <FormDescription>
          Leave <span className="font-semibold">end date</span> empty if you are
          currently working here.
        </FormDescription>
        <FormField
          control={form.control}
          name={`workExperiences.${index}.description`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Decription</FormLabel>
              <FormControl>
                <Textarea {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div>
          <Button
            onClick={() => {
              setOpen(true);
            }}
            type="button"
            className="w-full"
            variant="outline"
          >
            Smart fill from AI
          </Button>
        </div>
        <div className="flex justify-end">
          <Button
            variant="destructive"
            type="button"
            onClick={() => {
              remove(index);
            }}
          >
            Remove
          </Button>
        </div>
      </div>
    </>
  );
}
