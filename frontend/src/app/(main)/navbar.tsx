import ThemeToggle from "@/components/ui/theme-toggle";
// import { useAuth, UserButton } from "@clerk/nextjs";
// import { dark } from "@clerk/themes";
import { auth } from "@/auth";
import SignIn from "@/components/sign-in";
import { SignOut } from "@/components/sign-out";
import { BrainCircuitIcon } from "lucide-react";
import Link from "next/link";

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
