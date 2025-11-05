"use client";

import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function NavSignInButton() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/me`,
        {
          credentials: "include",
        }
      );
      setIsLoggedIn(res.ok);
    } catch (error) {
      setIsLoggedIn(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/logout`, {
        method: "POST",
        credentials: "include",
      });

      setIsLoggedIn(false);
      window.location.href = "/";
    } catch (error) {
      console.error("Error logging out", error);
    }
  };

  if (loading) {
    return <Button disabled>Loading...</Button>;
  }

  if (isLoggedIn) {
    return (
      <Button onClick={handleLogout} variant="outline">
        Sign Out
      </Button>
    );
  }

  return (
    <Button asChild>
      <Link href="/auth/login">Sign In</Link>
    </Button>
  );
}
