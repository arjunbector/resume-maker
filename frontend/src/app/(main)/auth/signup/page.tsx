"use client";

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
import { authSchema, AuthValues } from "@/lib/validations";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";

export default function SignUpPage() {
  const form = useForm<AuthValues>({
    resolver: zodResolver(authSchema),
    defaultValues: {
      email: "",
      password: "",
    },
    mode: "onChange",
  });
  const router = useRouter();
  const { isPending, mutate } = useMutation({
    mutationFn: async (values: AuthValues) => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/signup`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(values),
        }
      );
      if (!res.ok) {
        throw new Error("Failed to sign up");
      }
      
      return res.json();
    },
    onSuccess: (data) => {
        console.log(data)
      // Set the access token in cookies
      if (data.access_token) {
        console.log("Setting access token in cookie");
        document.cookie = `access_token=${data.access_token}; path=/; secure; samesite=none`;
      }
      window.location.href = "/";
    },
    onError: (error: any) => {
      console.error("Error signing up", error);
    },
  });
  return (
    <main className="container mx-auto min-h-screen flex flex-col justify-center items-center">
      <div className="shadow-lg border p-10 rounded-2xl">
        <h1 className="text-3xl font-bold text-center mb-10">Sign Up</h1>
        <Form {...form}>
          <form
            className="space-y-3"
            onSubmit={form.handleSubmit((values) => mutate(values))}
          >
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input {...field} autoFocus />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input {...field} type="password" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div>
              <Button className="w-full" disabled={isPending}>
                {isPending ? "Signing Up..." : "Sign Up"}
              </Button>
              <Button variant="link" className="w-full" asChild>
                <Link href="/auth/login">
                  Already have an account? Login here
                </Link>
              </Button>
            </div>
          </form>
        </Form>
      </div>
    </main>
  );
}
