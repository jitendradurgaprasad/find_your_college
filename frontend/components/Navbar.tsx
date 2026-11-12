"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Compass, 
  Search, 
  Cpu, 
  Scale, 
  ShieldCheck, 
  Activity, 
  Bookmark, 
  Settings,
  GraduationCap
} from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();

  const navLinks = [
    { name: "Search Colleges", href: "/search", icon: Search },
    { name: "Live Scanner", href: "/scanner", icon: Cpu },
    { name: "Compare", href: "/compare", icon: Scale },
    { name: "Data Quality", href: "/quality", icon: ShieldCheck },
    { name: "Monitoring", href: "/monitoring", icon: Activity },
    { name: "Saved", href: "/saved", icon: Bookmark },
    { name: "Admin", href: "/admin", icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="h-10 w-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:bg-blue-700 transition">
            <GraduationCap className="h-6 w-6" />
          </div>
          <div>
            <div className="text-lg font-bold tracking-tight text-slate-900 group-hover:text-blue-600 transition">
              Find Your <span className="text-blue-600">Collage</span>
            </div>
            <div className="text-[10px] text-slate-500 font-medium tracking-wide uppercase">
              Intelligence Platform
            </div>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
            return (
              <Link
                key={link.name}
                href={link.href}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition ${
                  isActive
                    ? "bg-blue-50 text-blue-700 font-semibold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? "text-blue-600" : "text-slate-400"}`} />
                {link.name}
              </Link>
            );
          })}
        </nav>

        {/* Action Button */}
        <div className="flex items-center gap-3">
          <Link
            href="/scanner"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium shadow-sm hover:bg-blue-700 active:scale-95 transition"
          >
            <Cpu className="h-4 w-4" />
            <span className="hidden sm:inline">Scan Institution</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
