import type React from "react"
import "./globals.css"
import type { Metadata } from "next"
import { inter, montserrat } from "./fonts"

export const metadata: Metadata = {
  title: "VolleyApi - Follow Your Matches",
  description: "Follow your favorite volleyball matches and see live stats",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="it">
      <body className={`${inter.variable} ${montserrat.variable} font-sans`}>{children}</body>
    </html>
  )
}
