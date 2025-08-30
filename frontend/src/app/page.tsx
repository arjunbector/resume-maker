import { auth } from "@/auth";
import SignIn from "@/components/sign-in";
import { SignOut } from "@/components/sign-out";

export default async function Home() {
  const session = await auth();
  if (session) {
    return (
      <main className="min-h-screen flex flex-col justify-center items-center">
        <div>signed in as {session.user?.name}</div>
        <SignOut />
      </main>
    );
  }
  return (
    <main className="min-h-screen flex justify-center items-center">
      <SignIn />
    </main>
  );
}
