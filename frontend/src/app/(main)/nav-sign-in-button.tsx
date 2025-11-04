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
      setIsLoggedIn(res.status === 200);
    } catch (error) {
      setIsLoggedIn(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      // Clear the access token cookie
      document.cookie =
        "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";

      setIsLoggedIn(false);
      window.location.reload();
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
