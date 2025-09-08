import useDimensions from "@/hooks/useDimensions";
import { cn } from "@/lib/utils";
import { formatDate } from "date-fns";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Badge } from "./ui/badge";

interface ResumePreviewProps {
  resumeData: any;
  className?: string;
  contentRef?: React.Ref<HTMLDivElement>;
}
export default function ResumePreview({
  resumeData,
  className,
  contentRef,
}: ResumePreviewProps) {
  console.log("resume preview me  =", resumeData);
  const containerRef = useRef<HTMLDivElement>(null);
  const { width } = useDimensions(containerRef);
  return (
    <div
      ref={containerRef}
      className={cn(
        "aspect-[210/297] h-fit w-full bg-white text-black",
        className
      )}
    >
      <div
        className={cn("space-y-6 p-6", !width && "hidden")}
        style={{
          zoom: (1 / 794) * width, // 210mm = 794px
        }}
        ref={contentRef}
        id="resume-preview-content"
      >
        <PersonalInfoHeader resumeData={resumeData} />
        {/* <SummarySection resumeData={resumeData} /> */}
        {/* <WorkExxperienceSection resumeData={resumeData} /> */}
        {/* <ProjectsSection resumeData={resumeData} /> */}
        {/* <EducationSection resumeData={resumeData} /> */}
        {/* <SkillsSection resumeData={resumeData} /> */}
      </div>
    </div>
  );
}

interface ResumeSectionProps {
  resumeData: any;
}

function PersonalInfoHeader({ resumeData }: ResumeSectionProps) {
  console.log("resume me values =", resumeData);
  const { firstName, lastName, jobTitle, city, country, phone, email } =
    resumeData;

  return (
    <div className="flex items-center gap-6">
      <div className="space-y-2.5">
        <div className="space-y-1">
          <p className="text-3xl font-bold">
            {firstName} {lastName}
          </p>
          <p className="font-medium">{jobTitle}</p>
          <p className="text-xs text-gray-500">
            {city}
            {city && country ? ", " : ""}
            {country}
            {(city || country) && (phone || email) ? " • " : ""}
            {[phone, email].filter(Boolean).join(" • ")}
          </p>
        </div>
      </div>
    </div>
  );
}

// function SummarySection({ resumeData }: ResumeSectionProps) {
//   const { summary, colorHex } = resumeData;
//   if (!summary) return null;
//   return (
//     <>
//       <hr
//         className="border-2"
//         style={{
//           borderColor: colorHex,
//         }}
//       />
//       <div className="break-inside-avoid space-y-3">
//         <p
//           className="text-lg font-semibold"
//           style={{
//             color: colorHex,
//           }}
//         >
//           Professional Summary
//         </p>
//         <div className="text-sm whitespace-pre-line">{summary}</div>
//       </div>
//     </>
//   );
// }

// function WorkExxperienceSection({ resumeData }: ResumePreviewProps) {
//   const { workExperiences, colorHex } = resumeData;
//   const workExperiencesNotEmpty = workExperiences?.filter(
//     (exp:any) => Object.values(exp).filter(Boolean).length > 0
//   );
//   if (!workExperiencesNotEmpty?.length) return null;
//   return (
//     <>
//       <hr
//         className="border-2"
//         style={{
//           borderColor: colorHex,
//         }}
//       />
//       <div className="space-y-3">
//         <p
//           className="text-lg font-semibold"
//           style={{
//             color: colorHex,
//           }}
//         >
//           Work Experience
//         </p>
//         {workExperiencesNotEmpty.map((exp, idx) => (
//           <div key={idx} className="break-after-avoid space-y-1">
//             <div
//               className="flex items-center justify-between text-sm font-semibold"
//               style={{
//                 color: colorHex,
//               }}
//             >
//               <span>{exp.position}</span>
//               {exp.startDate && (
//                 <span>
//                   {formatDate(exp.startDate, "MMMM yyyy")} -{" "}
//                   {exp.endDate
//                     ? formatDate(exp.endDate, "MMMM yyyy")
//                     : "Present"}
//                 </span>
//               )}
//             </div>
//             <p className="text-xs font-semibold">{exp.company}</p>
//             <div className="text-xs whitespace-pre-line">{exp.description}</div>
//           </div>
//         ))}
//       </div>
//     </>
//   );
// }

// function EducationSection({ resumeData }: ResumePreviewProps) {
//   const { educations, colorHex } = resumeData;
//   const educationsNotEmpty = educations?.filter(
//     (edu) => Object.values(edu).filter(Boolean).length > 0
//   );
//   if (!educationsNotEmpty?.length) return null;
//   return (
//     <>
//       <hr
//         className="border-2"
//         style={{
//           borderColor: colorHex,
//         }}
//       />
//       <div className="space-y-3">
//         <p
//           className="text-lg font-semibold"
//           style={{
//             color: colorHex,
//           }}
//         >
//           Education
//         </p>
//         {educationsNotEmpty.map((edu, idx) => (
//           <div key={idx} className="break-after-avoid space-y-1">
//             <div className="flex items-center justify-between text-sm font-semibold">
//               <span>{edu.degree}</span>
//               <div className="flex flex-col items-end">
//                 {edu.startDate && (
//                   <span>
//                     {formatDate(edu.startDate, "MMMM yyyy")}
//                     {edu.endDate
//                       ? ` -  ${formatDate(edu.endDate, "MMMM yyyy")}`
//                       : ""}
//                   </span>
//                 )}
//                 <p className="text-xs font-semibold">{edu.marks}</p>
//               </div>
//             </div>
//             <p className="text-xs font-semibold">{edu.school}</p>
//           </div>
//         ))}
//       </div>
//     </>
//   );
// }

// function ProjectsSection({ resumeData }: ResumePreviewProps) {
//   const { projects, colorHex } = resumeData;
//   const projectsNotEmpty = projects?.filter(
//     (project) => Object.values(project).filter(Boolean).length > 0
//   );
//   if (!projectsNotEmpty?.length) return null;
//   return (
//     <>
//       <hr
//         className="border-2"
//         style={{
//           borderColor: colorHex,
//         }}
//       />
//       <div className="space-y-3">
//         <p
//           className="text-lg font-semibold"
//           style={{
//             color: colorHex,
//           }}
//         >
//           Projects
//         </p>
//         {projectsNotEmpty.map((project, idx) => (
//           <div key={idx} className="break-after-avoid space-y-1">
//             <div className="flex items-center justify-between text-sm font-semibold">
//               <span>
//                 {project.link ? (
//                   <Link target="_blank" href={project.link}>
//                     {project.title}
//                   </Link>
//                 ) : (
//                   project.title
//                 )}
//               </span>
//               {project.startDate && (
//                 <span>
//                   {formatDate(project.startDate, "MMMM yyyy")}{" "}
//                   {project.endDate
//                     ? `- ${formatDate(project.endDate, "MMMM yyyy")}`
//                     : ""}
//                 </span>
//               )}
//             </div>
//             <div className="text-xs whitespace-pre-line">
//               {project.description}
//             </div>
//           </div>
//         ))}
//       </div>
//     </>
//   );
// }

// function SkillsSection({ resumeData }: ResumePreviewProps) {
//   const { skills, colorHex, borderStyle } = resumeData;
//   if (!skills?.length) return null;
//   return (
//     <>
//       <hr
//         className="border-2"
//         style={{
//           borderColor: colorHex,
//         }}
//       />
//       <div className="break-inside-avoid space-y-3">
//         <p className="text-lg font-semibold">Skills</p>
//         <div className="flex flex-wrap gap-2">
//           {skills.map((skill, idx) => (
//             <Badge
//               style={{
//                 backgroundColor: colorHex,

//                 borderRadius:
//                   borderStyle === BORDER_STYLES.SQUARE
//                     ? "0px"
//                     : borderStyle === BORDER_STYLES.CIRCLE
//                     ? "9999px"
//                     : "8px",
//               }}
//               key={idx}
//               className="rounded-md bg-black text-white"
//             >
//               {skill}
//             </Badge>
//           ))}
//         </div>
//       </div>
//     </>
//   );
// }
