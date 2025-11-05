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
import { cn } from "@/lib/utils";
import { researchSchema, ResearchValues } from "@/lib/validations";
import {
  closestCenter,
  DndContext,
  DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { restrictToVerticalAxis } from "@dnd-kit/modifiers";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { GripHorizontalIcon } from "lucide-react";
import { useEffect } from "react";
import { useFieldArray, useForm, UseFormReturn } from "react-hook-form";
import LoadingButton from "@/components/ui/loading-button";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";

export default function ResearchForm({
  resumeData,
  setResumeData,
}: EditorFormProps) {
  const form = useForm<ResearchValues>({
    resolver: zodResolver(researchSchema),
    defaultValues: {
      researchPapers: resumeData.researchPapers || [],
    },
  });

  // Reset form when resumeData changes

  useEffect(() => {
    const subscription = form.watch((values) => {
      const { isValid } = form.formState;
      console.log(isValid);
      if (!isValid && values) {
        setResumeData({
          ...resumeData,
          researchPapers: values.researchPapers?.filter(
            (paper): paper is NonNullable<typeof paper> => paper !== undefined
          ),
        });
      }
    });

    // return () => subscription.unsubscribe();
  }, [form, resumeData, setResumeData]);

  const { fields, append, remove, move } = useFieldArray({
    control: form.control,
    name: "researchPapers",
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

  const router = useRouter();
  const searchParams = useSearchParams();

  const { mutate, isPending } = useMutation({
    mutationFn: async (data: ResearchValues) => {
      // Transform frontend format to backend format
      const transformedResearch =
        data.researchPapers?.map((paper) => ({
          title: paper.title || "",
          venue: paper.venue || "",
          date: paper.date || "",
          description: paper.description || "",
          url: paper.url || "",
        })) || [];

      const payload = {
        research_work: transformedResearch,
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
        throw new Error("Failed to save research papers");
      }
    },
    onSuccess: () => {
      toast.success("Research papers saved successfully");
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set("step", "skills");
      router.push(`/editor?${newSearchParams.toString()}`);
    },
    onError: () => {
      toast.error("Failed to save research papers");
    },
  });

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div className="space-y-1.5 text-center">
        <h2 className="text-2xl font-semibold">Research Papers</h2>
        <p className="text-muted-foreground text-sm">
          Add your research publications here.
        </p>
      </div>
      <Form {...form}>
        <form
          className="space-y-3"
          onSubmit={form.handleSubmit((values) => mutate(values))}
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
                <ResearchItem
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
                  title: "",
                  venue: "",
                  date: "",
                  description: "",
                  url: "",
                });
              }}
            >
              Add Research Paper
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

interface ResearchItemProps {
  form: UseFormReturn<ResearchValues>;
  index: number;
  id: string;
  remove: (index: number) => void;
}

function ResearchItem({ form, index, remove, id }: ResearchItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  return (
    <div
      className={cn(
        "bg-background space-y-3 rounded-md border p-3",
        isDragging && "relative z-100 cursor-grab shadow-xl"
      )}
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
    >
      <div className="flex justify-between gap-2">
        <span className="font-semibold">Research Paper {index + 1}</span>
        <GripHorizontalIcon
          className="text-muted-foreground size-5 cursor-grab focus:outline-none"
          {...attributes}
          {...listeners}
        />
      </div>

      <FormField
        control={form.control}
        name={`researchPapers.${index}.title`}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Paper Title *</FormLabel>
            <FormControl>
              <Input
                {...field}
                placeholder="Enter the title of your research paper"
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name={`researchPapers.${index}.venue`}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Venue</FormLabel>
            <FormControl>
              <Input {...field} placeholder="Conference/Journal name" />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <div className="grid grid-cols-2 gap-3">
        <FormField
          control={form.control}
          name={`researchPapers.${index}.date`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Publication Date</FormLabel>
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
          name={`researchPapers.${index}.url`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Paper URL</FormLabel>
              <FormControl>
                <Input {...field} placeholder="https://..." />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormField
        control={form.control}
        name={`researchPapers.${index}.description`}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Description</FormLabel>
            <FormControl>
              <Textarea
                {...field}
                placeholder="Brief description in bulleted format"
                rows={4}
              />
            </FormControl>
            <FormDescription>
              Keep it short and use bullet points for key contributions
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

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
  );
}
