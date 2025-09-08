import { Button } from "@/components/ui/button";
import ThemeToggle from "@/components/ui/theme-toggle";
import logo from "@/public/globe.svg";
// import { useAuth, UserButton } from "@clerk/nextjs";
// import { dark } from "@clerk/themes";
import { BrainCircuitIcon, CreditCardIcon, Loader2Icon } from "lucide-react";
import { useTheme } from "next-themes";
import Image from "next/image";
import Link from "next/link";
import { useSession } from "next-auth/react";
import SignIn from "@/components/sign-in";
import { SignOut } from "@/components/sign-out";
import { auth } from "@/auth";

export default async function Navbar() {
  const session = await auth();

  //   const { userId } = useAuth();
  return (
    <header className="shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 p-3">
        <Link href="resumes" className="flex items-center gap-2">
          <BrainCircuitIcon className="size-8" />
          <span className="text-xl font-bold tracking-tight">Resume Maker</span>
        </Link>
        <div className="flex items-center gap-3">
          <ThemeToggle />
          {/* <UserButton
            appearance={{
              baseTheme: theme === "dark" ? dark : undefined,
              elements: {
                avatarBox: {
                  width: 35,
                  height: 35,
                },
              },
            }}
          >
            <UserButton.MenuItems>
              <UserButton.Link
                href="/billing"
                label="Billing"
                labelIcon={<CreditCardIcon className="size-4" />}
              />
            </UserButton.MenuItems>
          </UserButton> */}
          {session && <SignOut />}
          {!session && <SignIn />}
        </div>
      </div>
    </header>
  );
}
