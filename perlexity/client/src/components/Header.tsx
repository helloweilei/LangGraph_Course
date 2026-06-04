"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export function Header() {
  const pathname = usePathname();
  return (
    <header className="bg-linear-to-r from-violet-900 to-violet-800 text-white px-8 py-4 shadow-lg">
      <div className="flex items-center justify-between max-w-6xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-cyan-400 rounded-lg flex items-center justify-center font-bold">
            P
          </div>
          <h1 className="text-2xl font-bold">Perplexity 2.0</h1>
        </div>
        <nav className="flex gap-8">
          <Link
            href=""
            className="text-sm font-medium hover:text-cyan-400 transition"
          >
            HOME
          </Link>
          <Link
            href="/chat"
            className={
              "text-sm font-medium hover:text-cyan-400 transition " +
              `${pathname === "/chat" ? "text-cyan-400" : ""}`
            }
          >
            CHAT
          </Link>
          <Link
            href="/contacts"
            className="text-sm font-medium hover:text-cyan-400 transition"
          >
            CONTACTS
          </Link>
          <Link
            href="/settings"
            className="text-sm font-medium hover:text-cyan-400 transition"
          >
            SETTINGS
          </Link>
        </nav>
      </div>
    </header>
  );
}
