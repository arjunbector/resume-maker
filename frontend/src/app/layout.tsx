import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "./providers";
import { Toaster } from "sonner";
import { ThemeProvider } from "next-themes";
import Navbar from "./(main)/navbar";
import { SessionProvider } from "next-auth/react";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ResumeAI - AI-Powered Resume Builder",
  description: "Create ATS-optimized resumes with AI. Import data from LinkedIn, GitHub, and other platforms. Get personalized recommendations and real-time feedback for your job applications.",
  keywords: ["resume builder", "AI resume", "ATS optimization", "job application", "career", "professional resume"],
  authors: [{ name: "ResumeAI Team" }],
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
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://resumeai.com',
    title: 'ResumeAI - AI-Powered Resume Builder',
    description: 'Create ATS-optimized resumes with AI. Import data from LinkedIn, GitHub, and other platforms.',
    siteName: 'ResumeAI',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ResumeAI - AI-Powered Resume Builder',
    description: 'Create ATS-optimized resumes with AI. Import data from LinkedIn, GitHub, and other platforms.',
    creator: '@resumeai',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
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
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
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
