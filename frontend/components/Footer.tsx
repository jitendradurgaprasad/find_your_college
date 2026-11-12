import Link from "next/link";
import { GraduationCap, ShieldCheck, Database, Globe, ExternalLink } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50 text-slate-600 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Info */}
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <GraduationCap className="h-5 w-5" />
              </div>
              <span className="font-bold text-slate-900 text-lg">Find Your Collage</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              An intelligent college and university discovery platform crawling publicly accessible official websites to extract structured, verified educational intelligence.
            </p>
            <div className="flex items-center gap-2 text-xs text-emerald-600 font-medium">
              <ShieldCheck className="h-4 w-4" />
              <span>100% Source Traceability Guarantee</span>
            </div>
          </div>

          {/* Platform Discovery */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 tracking-wider uppercase mb-3">Discovery</h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/search" className="hover:text-blue-600 transition">Search All Colleges</Link></li>
              <li><Link href="/search?degree_type=Undergraduate" className="hover:text-blue-600 transition">B.Tech & UG Programs</Link></li>
              <li><Link href="/search?degree_type=Postgraduate" className="hover:text-blue-600 transition">M.Tech & MBA Programs</Link></li>
              <li><Link href="/search?admission_status=OPEN" className="hover:text-blue-600 transition">Open Admissions 2025</Link></li>
              <li><Link href="/search?has_scholarship=true" className="hover:text-blue-600 transition">Scholarships & Aid</Link></li>
            </ul>
          </div>

          {/* Intelligence Tools */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 tracking-wider uppercase mb-3">Intelligence</h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/scanner" className="hover:text-blue-600 transition">Live Website Scanner</Link></li>
              <li><Link href="/compare" className="hover:text-blue-600 transition">Side-by-Side Comparison</Link></li>
              <li><Link href="/quality" className="hover:text-blue-600 transition">Data Quality Dashboard</Link></li>
              <li><Link href="/monitoring" className="hover:text-blue-600 transition">Change Detection Audit</Link></li>
              <li><Link href="/admin" className="hover:text-blue-600 transition">Administrative Operations</Link></li>
            </ul>
          </div>

          {/* Architecture & Compliance */}
          <div>
            <h4 className="text-xs font-semibold text-slate-900 tracking-wider uppercase mb-3">Integrity & Standards</h4>
            <p className="text-xs text-slate-500 leading-relaxed mb-3">
              Strictly adheres to <code className="text-blue-600">robots.txt</code>, SSRF prevention, request rate limiting, and authentic citation policies. No fabricated numbers or dates.
            </p>
            <div className="text-[11px] text-slate-400">
              Built with FastAPI, BeautifulSoup, Supabase PostgreSQL, and Next.js.
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© {new Date().getFullYear()} Find Your Collage Intelligence. Educational discovery engine.</p>
          <div className="flex items-center gap-6">
            <span>Discover colleges. Explore opportunities. Make informed decisions.</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
