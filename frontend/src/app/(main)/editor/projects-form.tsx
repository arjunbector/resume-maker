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
import { projectsSchema, ProjectsValues } from "@/lib/validations";
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
export default function ProjectsForm({
  resumeData,
  setResumeData,
}: EditorFormProps) {
  const form = useForm<ProjectsValues>({
    resolver: zodResolver(projectsSchema),
    defaultValues: {
      projects: resumeData.projects || [],
    },
  });

  useEffect(() => {
    // Create a subscription to watch form changes
    const subscription = form.watch((values) => {
      const { isValid } = form.formState;

      // Only update parent state when form is valid
      if (isValid && values) {
        setResumeData({
          ...resumeData,
          ...values,
          projects: values.projects?.filter(
            (project): project is NonNullable<typeof project> =>
              project !== undefined
          ),
        });
      }
    });

    // Clean up subscription on unmount
    return () => subscription.unsubscribe();
  }, [form, resumeData, setResumeData]);

  const { fields, append, remove, move } = useFieldArray({
    control: form.control,
    name: "projects",
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
    mutationFn: async (data: ProjectsValues) => {
      // Transform frontend format to backend format
      const transformedProjects = data.projects?.map((project) => ({
        name: project.title || "",
        description: project.description || "",
        technologies: [], // You might want to add a technologies field to the form
        url: project.link || "",
        start_date: project.startDate || "",
        end_date: project.endDate || "",
      })) || [];

      const payload = {
        projects: transformedProjects,
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
        throw new Error("Failed to save projects info");
      }
    },
    onSuccess: () => {
      toast.success("Projects saved successfully");
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set("step", "skills");
      router.push(`/editor?${newSearchParams.toString()}`);
    },
    onError: () => {
      toast.error("Failed to save projects");
    },
  });

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div className="space-y-1.5 text-center">
        <h2 className="text-2xl font-semibold">Projects</h2>
        <p className="text-muted-foreground text-sm">Add your projects here.</p>
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
                <ProjectsItem
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
                  link: "",
                  startDate: "",
                  endDate: "",
                  description: "",
                });
              }}
            >
              Add Project
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

interface ProjectsItemProps {
  form: UseFormReturn<ProjectsValues>;
  index: number;
  id: string;
  remove: (index: number) => void;
}
function ProjectsItem({ form, index, remove, id }: ProjectsItemProps) {
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
        <span className="font-semibold">Project {index + 1}</span>
        <GripHorizontalIcon
          className="text-muted-foreground size-5 cursor-grab focus:outline-none"
          {...attributes}
          {...listeners}
        />
      </div>
      <FormField
        control={form.control}
        name={`projects.${index}.title`}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Project Title</FormLabel>
            <FormControl>
              <Input {...field} autoFocus />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name={`projects.${index}.link`}
        render={({ field }) => (
          <FormItem>
            <FormLabel>Project Link</FormLabel>
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
          name={`projects.${index}.startDate`}
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
          name={`projects.${index}.endDate`}
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
        name={`projects.${index}.description`}
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
