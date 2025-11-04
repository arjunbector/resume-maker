import ThemeToggle from "@/components/ui/theme-toggle";
// import { useAuth, UserButton } from "@clerk/nextjs";
// import { dark } from "@clerk/themes";
import { BrainCircuitIcon } from "lucide-react";
import Link from "next/link";
import NavSignInButton from "./nav-sign-in-button";

export default async function Navbar() {
  return (
    <header className="shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 p-3">
        <Link href="/" className="flex items-center gap-2">
          <BrainCircuitIcon className="size-8" />
          <span className="text-xl font-bold tracking-tight">Resume Maker</span>
        </Link>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <NavSignInButton />
        </div>
      </div>
    </header>
  );
}
