import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "./providers";
import { Toaster } from "sonner";
import { ThemeProvider } from "next-themes";
import Navbar from "./(main)/navbar";
import { SessionProvider } from "next-auth/react";



export const metadata: Metadata = {
  title: "ResumeAI - AI-Powered Resume Builder",
  description: "Create ATS-optimized resumes with AI. Import data from LinkedIn, GitHub, and other platforms. Get personalized recommendations and real-time feedback for your job applications.",
  keywords: ["resume builder", "AI resume", "ATS optimization", "job application", "career", "professional resume"],
  authors: [{ name: "Arjun Bector" }],
  creator: "ResumeAI",
  publisher: "ResumeAI",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={"antialiased"}
      >
        <SessionProvider>
          <Providers>
            <ThemeProvider
              attribute="class"
              defaultTheme="system"
              enableSystem
              disableTransitionOnChange
            >
              <Navbar />
              {children}
            </ThemeProvider>
            <Toaster />
          </Providers>
        </SessionProvider>
      </body>
    </html>
  );
}
