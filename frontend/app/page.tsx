"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  Search, 
  MapPin, 
  Cpu, 
  ShieldCheck, 
  BookOpen, 
  Award, 
  GraduationCap, 
  Building2, 
  CheckCircle2, 
  ArrowRight, 
  Layers, 
  Sparkles,
  TrendingUp,
  Clock,
  Compass
} from "lucide-react";
import CollegeCard from "@/components/CollegeCard";
import CollegeSearchAutocomplete from "@/components/CollegeSearchAutocomplete";
import { fetchUniversities, fetchDataQuality, UniversitySummary, QualityMetrics } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [recentColleges, setRecentColleges] = useState<UniversitySummary[]>([]);
  const [qualityStats, setQualityStats] = useState<QualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [univData, qualityData] = await Promise.all([
          fetchUniversities({ page_size: 6 }),
          fetchDataQuality()
        ]);
        if (univData && univData.results) {
          setRecentColleges(univData.results);
        }
        if (qualityData) {
          setQualityStats(qualityData);
        }
      } catch (err) {
        console.error("Failed to load initial data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?query=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      router.push("/search");
    }
  };

  const discoveryCategories = [
    { title: "Engineering & Tech", query: "Engineering", icon: Cpu, count: "B.Tech, M.Tech, AI & Robotics" },
    { title: "Artificial Intelligence", query: "Artificial Intelligence", icon: Sparkles, count: "AI, Machine Learning, Data Science" },
    { title: "Management & MBA", query: "Management", icon: TrendingUp, count: "MBA, BBA, Finance, Analytics" },
    { title: "Research & PhD", query: "Research", icon: BookOpen, count: "Doctoral Programs & Funded Labs" },
    { title: "Open Admissions", filter: "admission_status=OPEN", icon: Clock, count: "Currently Active Applications" },
    { title: "Scholarships Available", filter: "has_scholarship=true", icon: Award, count: "Institutional & Merit Concessions" },
  ];

  const popularLocations = [
    { city: "Mumbai", state: "Maharashtra" },
    { city: "Hyderabad", state: "Telangana" },
    { city: "Bengaluru", state: "Karnataka" },
    { city: "Delhi", state: "Delhi NCR" },
    { city: "Chennai", state: "Tamil Nadu" },
    { city: "Pilani", state: "Rajasthan" },
  ];

  return (
    <div className="space-y-16 pb-16">
      {/* HERO SECTION */}
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-50/70 via-white to-slate-50 border-b border-slate-200 pt-16 pb-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          {/* Trust Pill */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100/70 border border-blue-200 text-blue-800 text-xs font-semibold shadow-sm">
            <ShieldCheck className="h-4 w-4 text-blue-600" />
            <span>Autonomous Web Scraping & Fact Extraction Engine</span>
          </div>

          {/* Master Hero Heading & Description (Section 9 Requirement) */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Find the Right College for Your Future.
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-600 leading-relaxed font-normal">
            Discover colleges, explore courses, compare opportunities, and stay informed about admissions and scholarships — all in one place.
          </p>

          {/* Main Search Bar with Real-time Auto-Suggest */}
          <div className="max-w-3xl mx-auto pt-4">
            <form onSubmit={handleSearchSubmit} className="relative flex items-center shadow-lg rounded-2xl bg-white border border-slate-200 p-2 focus-within:ring-2 focus-within:ring-blue-600 focus-within:border-blue-600 transition">
              <CollegeSearchAutocomplete
                value={searchQuery}
                onChange={setSearchQuery}
                autoNavigate={true}
                placeholder="Type college name (e.g. BITS Pilani, IIT Bombay, Stanford)..."
                inputClassName="py-3 text-sm sm:text-base bg-transparent border-0"
              />
              <button
                type="submit"
                className="flex-shrink-0 inline-flex items-center gap-1.5 px-6 py-3 rounded-xl bg-blue-600 text-white font-semibold text-sm hover:bg-blue-700 active:scale-95 transition shadow-sm ml-2"
              >
                <span>Search</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </form>

            {/* Quick Actions & AI Search Pill */}
            <div className="flex items-center justify-center gap-2 mt-4 flex-wrap text-xs text-slate-500">
              <button
                type="button"
                onClick={() => router.push(`/search?ai=true&query=${encodeURIComponent(searchQuery || "Top engineering colleges with open admissions and scholarships")}`)}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold shadow-sm hover:from-blue-700 hover:to-indigo-700 transition"
              >
                <Sparkles className="h-3.5 w-3.5" />
                <span>AI Smart Search (Gemini)</span>
              </button>
              <span className="font-medium text-slate-400 ml-2">Quick Locations:</span>
              {popularLocations.map((loc) => (
                <button
                  key={loc.city}
                  type="button"
                  onClick={() => router.push(`/search?city=${encodeURIComponent(loc.city)}`)}
                  className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 hover:border-blue-400 hover:text-blue-600 transition"
                >
                  {loc.city}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* PLATFORM METRICS BAR */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <div className="text-center p-3 border-r border-slate-100 last:border-0">
            <div className="text-2xl sm:text-3xl font-extrabold text-blue-600">
              {qualityStats?.total_institutions || "3+"}
            </div>
            <div className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wide">
              Institutions Scanned
            </div>
          </div>

          <div className="text-center p-3 border-r border-slate-100 last:border-0">
            <div className="text-2xl sm:text-3xl font-extrabold text-emerald-600">
              {qualityStats?.total_extracted_records || "45+"}
            </div>
            <div className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wide">
              Verified Facts Extracted
            </div>
          </div>

          <div className="text-center p-3 border-r border-slate-100 last:border-0">
            <div className="text-2xl sm:text-3xl font-extrabold text-indigo-600">
              {qualityStats?.total_crawled_pages || "25+"}
            </div>
            <div className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wide">
              Official Pages Audited
            </div>
          </div>

          <div className="text-center p-3">
            <div className="text-2xl sm:text-3xl font-extrabold text-amber-600">
              {qualityStats?.average_completeness_score ? `${qualityStats.average_completeness_score}%` : "94%"}
            </div>
            <div className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wide">
              Avg Completeness Score
            </div>
          </div>
        </div>
      </section>

      {/* FEATURED DISCOVERY CATEGORIES */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
              Featured Discovery Pathways
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Explore specialized educational opportunities indexed directly from institutional portals.
            </p>
          </div>
          <Link href="/search" className="hidden sm:flex items-center gap-1 text-sm font-semibold text-blue-600 hover:text-blue-800">
            <span>View All</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {discoveryCategories.map((cat) => {
            const Icon = cat.icon;
            const targetUrl = cat.filter ? `/search?${cat.filter}` : `/search?query=${encodeURIComponent(cat.query || "")}`;
            return (
              <Link
                key={cat.title}
                href={targetUrl}
                className="group p-5 rounded-2xl bg-white border border-slate-200 hover:border-blue-400 hover:shadow-md transition duration-200 flex items-start gap-4"
              >
                <div className="h-12 w-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-600 group-hover:text-white transition">
                  <Icon className="h-6 w-6" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-slate-900 group-hover:text-blue-600 transition truncate text-sm sm:text-base">
                    {cat.title}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                    {cat.count}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* RECENTLY INDEXED INSTITUTIONS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
              Recently Indexed Institutions
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Structured datasets freshly extracted and validated from official university websites.
            </p>
          </div>
          <Link href="/search" className="flex items-center gap-1 text-sm font-semibold text-blue-600 hover:text-blue-800">
            <span>Browse Directory</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-64 rounded-2xl bg-slate-100 animate-pulse border border-slate-200" />
            ))}
          </div>
        ) : recentColleges.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recentColleges.map((col) => (
              <CollegeCard key={col.id} college={col} />
            ))}
          </div>
        ) : (
          <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
            <Building2 className="h-10 w-10 text-slate-400 mx-auto mb-3" />
            <p className="text-sm font-medium text-slate-700">No institutions found.</p>
            <Link href="/scanner" className="mt-3 inline-block text-xs font-semibold text-blue-600 hover:underline">
              Scan your first college website now →
            </Link>
          </div>
        )}
      </section>

      {/* HOW THE PLATFORM WORKS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-8 sm:p-12 rounded-3xl bg-slate-900 text-white space-y-10">
          <div className="text-center max-w-2xl mx-auto space-y-3">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-400 border border-blue-400/30">
              Autonomous Pipeline
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              How Find Your Collage Works
            </h2>
            <p className="text-sm sm:text-base text-slate-400 leading-relaxed">
              We extract, cross-verify, and structure educational intelligence directly from authorized institutional web pages.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-slate-300">
            <div className="p-5 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-3">
              <div className="h-10 w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                01
              </div>
              <h3 className="font-bold text-white text-base">URL & Robots Check</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Checks robots.txt permissions, discover sitemap.xml, applies SSRF security filters, and validates domain ownership.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-3">
              <div className="h-10 w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                02
              </div>
              <h3 className="font-bold text-white text-base">Breadth Crawling</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Respectful, rate-limited crawling parses HTML structures, prospectus tables, and admission circular PDFs.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-3">
              <div className="h-10 w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                03
              </div>
              <h3 className="font-bold text-white text-base">Structured Extraction</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Heuristic classifiers extract degree programs, fee matrices, verified admission cycles, faculty directories, and placement reports.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-800/60 border border-slate-700/60 space-y-3">
              <div className="h-10 w-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                04
              </div>
              <h3 className="font-bold text-white text-base">Traceability & Audit</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Every extracted fact retains verbatim source citations, timestamped snapshots, and conflict resolution flags.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
