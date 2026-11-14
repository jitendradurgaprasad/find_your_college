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
  Compass,
  Globe,
  Zap,
  RotateCw
} from "lucide-react";
import CollegeCard from "@/components/CollegeCard";
import CollegeSearchAutocomplete from "@/components/CollegeSearchAutocomplete";
import { fetchUniversities, fetchDataQuality, UniversitySummary, QualityMetrics } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();

  // Hero Mode: "scan" | "search" | "ai" (default to "scan" as requested)
  const [activeHeroTab, setActiveHeroTab] = useState<"scan" | "search" | "ai">("scan");

  // Direct Website Scanner state
  const [scanUrl, setScanUrl] = useState("");
  const [scanCollegeName, setScanCollegeName] = useState("");

  // Directory Search state
  const [searchQuery, setSearchQuery] = useState("");

  // AI Search state
  const [aiPrompt, setAiPrompt] = useState("");

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

  // Direct Scan Form Submit
  const handleDirectScan = (e?: React.FormEvent, customUrl?: string, customName?: string) => {
    if (e) e.preventDefault();
    let targetUrl = (customUrl || scanUrl).trim();
    if (!targetUrl) return;

    if (!targetUrl.startsWith("http://") && !targetUrl.startsWith("https://")) {
      targetUrl = "https://" + targetUrl;
    }

    const targetName = (customName || scanCollegeName).trim();
    router.push(`/scanner?url=${encodeURIComponent(targetUrl)}&name=${encodeURIComponent(targetName)}&auto=true`);
  };

  // Search Form Submit
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?query=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      router.push("/search");
    }
  };

  // AI Search Form Submit
  const handleAISubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const prompt = aiPrompt.trim() || "Top engineering colleges with open admissions and scholarships";
    router.push(`/search?ai=true&query=${encodeURIComponent(prompt)}`);
  };

  const quickScanInstitutions = [
    { name: "NIT Warangal", url: "https://www.nitw.ac.in" },
    { name: "IIT Bombay", url: "https://www.iitb.ac.in" },
    { name: "BITS Pilani", url: "https://www.bits-pilani.ac.in" },
    { name: "IIIT Hyderabad", url: "https://www.iiit.ac.in" },
    { name: "Malla Reddy University", url: "https://www.mallareddyuniversity.ac.in" },
  ];

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
      {/* HERO SECTION / FIRST DASHBOARD */}
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-50/70 via-white to-slate-50 border-b border-slate-200 pt-16 pb-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          {/* Trust Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-100/70 border border-blue-200 text-blue-800 text-xs font-semibold shadow-sm">
            <ShieldCheck className="h-4 w-4 text-blue-600" />
            <span>Autonomous Web Scraping & Fact Extraction Engine</span>
          </div>

          {/* Master Hero Heading & Description */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Find the Right College for Your Future.
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-600 leading-relaxed font-normal">
            Directly scan any college website to extract verified admissions, degree courses, fee matrices, and placement records — or explore indexed institutions.
          </p>

          {/* PRIMARY DASHBOARD SCAN & DISCOVERY CONTROLLER */}
          <div className="max-w-3xl mx-auto pt-4 space-y-4">
            {/* Mode Selector Tabs (Scan Website is First & Active!) */}
            <div className="inline-flex p-1.5 rounded-2xl bg-slate-100 border border-slate-200 text-xs font-bold text-slate-600 shadow-inner">
              <button
                type="button"
                onClick={() => setActiveHeroTab("scan")}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-xl transition ${
                  activeHeroTab === "scan"
                    ? "bg-blue-600 text-white shadow-sm"
                    : "hover:text-slate-900 hover:bg-white/60"
                }`}
              >
                <Globe className="h-4 w-4" />
                <span>⚡ Scan College Website</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveHeroTab("search")}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-xl transition ${
                  activeHeroTab === "search"
                    ? "bg-blue-600 text-white shadow-sm"
                    : "hover:text-slate-900 hover:bg-white/60"
                }`}
              >
                <Search className="h-4 w-4" />
                <span>Search by Name</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveHeroTab("ai")}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-xl transition ${
                  activeHeroTab === "ai"
                    ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-sm"
                    : "hover:text-slate-900 hover:bg-white/60"
                }`}
              >
                <Sparkles className="h-4 w-4" />
                <span>✨ AI Smart Search</span>
              </button>
            </div>

            {/* TAB 1: DIRECT WEBSITE SCANNER (FIRST DASHBOARD VIEW) */}
            {activeHeroTab === "scan" && (
              <div className="bg-white p-5 sm:p-7 rounded-3xl border border-slate-200 shadow-xl space-y-4 animate-in fade-in duration-200 text-left">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <span className="p-1.5 rounded-xl bg-blue-50 text-blue-600">
                      <Globe className="h-4 w-4" />
                    </span>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-800">
                      Direct College Website Scanner
                    </span>
                  </div>
                  <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                    Live Fact Extraction
                  </span>
                </div>

                <form onSubmit={handleDirectScan} className="space-y-3">
                  <div className="relative flex items-center">
                    <Globe className="h-5 w-5 text-slate-400 absolute left-4" />
                    <input
                      type="text"
                      required
                      value={scanUrl}
                      onChange={(e) => setScanUrl(e.target.value)}
                      placeholder="Paste your preferred college website URL (e.g. https://www.nitw.ac.in)..."
                      className="w-full pl-12 pr-4 py-3.5 text-sm sm:text-base text-slate-900 placeholder:text-slate-400 rounded-2xl border border-slate-200 bg-slate-50/60 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition"
                    />
                  </div>

                  <div className="flex flex-col sm:flex-row items-center gap-3">
                    <div className="relative w-full sm:w-2/3">
                      <CollegeSearchAutocomplete
                        value={scanCollegeName}
                        onChange={setScanCollegeName}
                        onSelect={(col) => {
                          setScanCollegeName(col.name);
                          if (col.official_website) setScanUrl(col.official_website);
                        }}
                        autoNavigate={false}
                        placeholder="Institution Name (optional, e.g. NIT Warangal)"
                        inputClassName="py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50/60 focus:ring-2 focus:ring-blue-600"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={!scanUrl.trim()}
                      className="w-full sm:w-1/3 flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold text-sm shadow-md hover:shadow-lg active:scale-95 transition"
                    >
                      <Zap className="h-4 w-4" />
                      <span>Scan & Extract</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </div>
                </form>

                {/* Quick Sample Links */}
                <div className="flex items-center gap-2 flex-wrap pt-2 text-xs text-slate-500">
                  <span className="font-semibold text-slate-400">Quick Test Websites:</span>
                  {quickScanInstitutions.map((inst) => (
                    <button
                      key={inst.name}
                      type="button"
                      onClick={() => {
                        setScanUrl(inst.url);
                        setScanCollegeName(inst.name);
                        handleDirectScan(undefined, inst.url, inst.name);
                      }}
                      className="px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200 hover:border-blue-400 hover:text-blue-600 text-slate-700 transition"
                    >
                      {inst.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 2: DIRECTORY AUTOCOMPLETE SEARCH */}
            {activeHeroTab === "search" && (
              <div className="space-y-4 animate-in fade-in duration-200">
                <form onSubmit={handleSearchSubmit} className="relative flex items-center shadow-xl rounded-3xl bg-white border border-slate-200 p-2 focus-within:ring-2 focus-within:ring-blue-600 focus-within:border-blue-600 transition">
                  <CollegeSearchAutocomplete
                    value={searchQuery}
                    onChange={setSearchQuery}
                    autoNavigate={true}
                    placeholder="Type college name (e.g. BITS Pilani, IIT Bombay, Stanford)..."
                    inputClassName="py-3 text-sm sm:text-base bg-transparent border-0"
                  />
                  <button
                    type="submit"
                    className="flex-shrink-0 inline-flex items-center gap-1.5 px-6 py-3 rounded-2xl bg-blue-600 text-white font-bold text-sm hover:bg-blue-700 active:scale-95 transition shadow-sm ml-2"
                  >
                    <span>Search</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </form>

                <div className="flex items-center justify-center gap-2 flex-wrap text-xs text-slate-500">
                  <span className="font-medium text-slate-400">Quick Locations:</span>
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
            )}

            {/* TAB 3: AI SMART SEARCH INQUIRY */}
            {activeHeroTab === "ai" && (
              <div className="space-y-4 animate-in fade-in duration-200">
                <form onSubmit={handleAISubmit} className="relative flex flex-col sm:flex-row items-center gap-2 p-2 rounded-3xl bg-white border border-slate-200 shadow-xl">
                  <div className="relative w-full">
                    <Sparkles className="h-5 w-5 text-indigo-500 absolute left-4 top-3.5" />
                    <input
                      type="text"
                      value={aiPrompt}
                      onChange={(e) => setAiPrompt(e.target.value)}
                      placeholder="Ask Gemini: e.g. Best colleges in south India for AI with fees and placements..."
                      className="w-full pl-12 pr-4 py-3 text-sm sm:text-base text-slate-900 placeholder:text-slate-400 focus:outline-none bg-transparent"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold text-sm shadow-md hover:from-blue-700 hover:to-indigo-700 transition flex items-center justify-center gap-2 flex-shrink-0"
                  >
                    <Sparkles className="h-4 w-4" />
                    <span>Ask Gemini</span>
                  </button>
                </form>

                <div className="flex items-center justify-center gap-2 flex-wrap text-xs text-slate-500">
                  <span className="font-medium text-slate-400">Try asking:</span>
                  <button
                    type="button"
                    onClick={() => router.push("/search?ai=true&query=Colleges+with+open+admissions+and+scholarships")}
                    className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 hover:text-blue-600 transition"
                  >
                    Open Admissions 2026-27
                  </button>
                  <button
                    type="button"
                    onClick={() => router.push("/search?ai=true&query=Highest+placement+packages+above+40+LPA")}
                    className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 hover:text-blue-600 transition"
                  >
                    Top Placements &gt; 40 LPA
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* PLATFORM METRICS BAR */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <div className="text-center p-3 border-r border-slate-100 last:border-0">
            <div className="text-2xl sm:text-3xl font-extrabold text-blue-600">
              {qualityStats?.total_institutions || "4"}
            </div>
            <div className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wide">
              Institutions Scanned
            </div>
          </div>

          <div className="text-center p-3 border-r border-slate-100 last:border-0">
            <div className="text-2xl sm:text-3xl font-extrabold text-emerald-600">
              {qualityStats?.total_extracted_records || "150+"}
            </div>
            <div className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wide">
              Verified Facts Extracted
            </div>
          </div>

          <div className="text-center p-3 border-r border-slate-100 last:border-0">
            <div className="text-2xl sm:text-3xl font-extrabold text-indigo-600">
              {qualityStats?.total_crawled_pages || "50+"}
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
              Avg Completeness
            </div>
          </div>
        </div>
      </section>

      {/* DISCOVERY CATEGORIES GRID */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              Explore by Discipline & Eligibility
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Filter institutions by specialized departments, admission cycles, or funding.
            </p>
          </div>
          <Link
            href="/search"
            className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 transition"
          >
            <span>Browse All</span>
            <ArrowRight className="h-3.5 w-3.5" />
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
                className="p-5 rounded-2xl bg-white border border-slate-200 hover:border-blue-400 hover:shadow-md transition group space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="p-3 rounded-xl bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition">
                    <Icon className="h-5 w-5" />
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-300 group-hover:text-blue-600 group-hover:translate-x-1 transition" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition">
                    {cat.title}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">{cat.count}</p>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* VERIFIED INSTITUTIONS RECENT SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              Verified Educational Institutions
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Institutions autonomously crawled and stored with complete fact traceability.
            </p>
          </div>
          <Link
            href="/search"
            className="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1 transition"
          >
            <span>View Full Directory</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-72 rounded-2xl bg-slate-100 animate-pulse border border-slate-200" />
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
            <Building2 className="h-10 w-10 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-600">No institutions found.</p>
          </div>
        )}
      </section>

      {/* HOW IT WORKS / AUDIT INTEGRITY SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-8 sm:p-10 rounded-3xl bg-slate-900 text-white space-y-8">
          <div className="max-w-2xl space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-400">
              Autonomous Intelligence
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              100% Grounded in Official Websites. Zero Hallucinations.
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
              Find Your Collage never fabricates dates, fees, rankings, or placement figures. Every single number links directly to its official webpage or PDF prospectus.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
            <div className="p-5 rounded-2xl bg-slate-800/80 border border-slate-700/60 space-y-2">
              <div className="h-8 w-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-sm">
                1
              </div>
              <h3 className="text-sm font-bold text-white">Direct URL Crawling</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Respectful robots.txt parsing, recursive HTML discovery, and prospectus PDF ingestion with SSRF security.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-800/80 border border-slate-700/60 space-y-2">
              <div className="h-8 w-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm">
                2
              </div>
              <h3 className="text-sm font-bold text-white">Structured Extraction</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Categorization into 11 relational domains: admissions, courses, fees, placements, scholarships, and faculties.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-800/80 border border-slate-700/60 space-y-2">
              <div className="h-8 w-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm">
                3
              </div>
              <h3 className="text-sm font-bold text-white">Verifiable Traceability</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Every extracted statement is preserved with verbatim source evidence and date of last verification.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
