"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  Search, 
  Filter, 
  RotateCcw, 
  SlidersHorizontal, 
  Building2, 
  MapPin, 
  ChevronLeft, 
  ChevronRight,
  GraduationCap,
  Sparkles,
  Key,
  Eye,
  EyeOff,
  ExternalLink,
  BookOpen,
  Award,
  Compass,
  ArrowRight,
  CheckCircle2,
  Loader2
} from "lucide-react";
import CollegeCard from "@/components/CollegeCard";
import CollegeSearchAutocomplete from "@/components/CollegeSearchAutocomplete";
import { 
  fetchUniversities, 
  performAISearch, 
  UniversitySummary, 
  AISearchResponse, 
  RecommendedInstitution 
} from "@/lib/api";

function SearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Mode: "directory" | "ai"
  const [searchMode, setSearchMode] = useState<"directory" | "ai">(
    searchParams.get("ai") === "true" ? "ai" : "directory"
  );

  // Filters State
  const [query, setQuery] = useState(searchParams.get("query") || "");
  const [country, setCountry] = useState(searchParams.get("country") || "");
  const [state, setState] = useState(searchParams.get("state") || "");
  const [city, setCity] = useState(searchParams.get("city") || "");
  const [institutionType, setInstitutionType] = useState(searchParams.get("institution_type") || "");
  const [admissionStatus, setAdmissionStatus] = useState(searchParams.get("admission_status") || "");
  const [degreeType, setDegreeType] = useState(searchParams.get("degree_type") || "");
  const [hasScholarship, setHasScholarship] = useState(searchParams.get("has_scholarship") === "true");

  // Pagination & Results State
  const [currentPage, setCurrentPage] = useState(1);
  const [results, setResults] = useState<UniversitySummary[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // AI Smart Search State
  const [aiQuery, setAiQuery] = useState(searchParams.get("query") || "");
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [showApiKey, setShowApiKey] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState<AISearchResponse | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  // Load saved Gemini API Key from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedKey = localStorage.getItem("FIND_YOUR_COLLEGE_GEMINI_KEY") || "";
      setGeminiApiKey(savedKey);
    }
  }, []);

  const handleApiKeyChange = (newKey: string) => {
    setGeminiApiKey(newKey);
    if (typeof window !== "undefined") {
      localStorage.setItem("FIND_YOUR_COLLEGE_GEMINI_KEY", newKey);
    }
  };

  // Sync state when URL params change
  useEffect(() => {
    const q = searchParams.get("query") || "";
    setQuery(q);
    if (searchParams.get("ai") === "true") {
      setSearchMode("ai");
      setAiQuery(q);
    }
    setCountry(searchParams.get("country") || "");
    setState(searchParams.get("state") || "");
    setCity(searchParams.get("city") || "");
    setInstitutionType(searchParams.get("institution_type") || "");
    setAdmissionStatus(searchParams.get("admission_status") || "");
    setDegreeType(searchParams.get("degree_type") || "");
    setHasScholarship(searchParams.get("has_scholarship") === "true");
  }, [searchParams]);

  // Execute Directory Search
  useEffect(() => {
    if (searchMode !== "directory") return;

    async function loadResults() {
      setLoading(true);
      try {
        const data = await fetchUniversities({
          query: query.trim() || undefined,
          country: country || undefined,
          state: state || undefined,
          city: city || undefined,
          institution_type: institutionType || undefined,
          admission_status: admissionStatus || undefined,
          degree_type: degreeType || undefined,
          page: currentPage,
          page_size: 9
        });
        setResults(data.results || []);
        setTotalCount(data.total || 0);
        setTotalPages(data.total_pages || 1);
      } catch (err) {
        console.error("Search failed:", err);
      } finally {
        setLoading(false);
      }
    }
    loadResults();
  }, [query, country, state, city, institutionType, admissionStatus, degreeType, hasScholarship, currentPage, searchMode]);

  // Handle AI Search Execution
  const executeAISearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!aiQuery.trim()) return;

    setAiLoading(true);
    setAiError(null);
    try {
      const res = await performAISearch(aiQuery, geminiApiKey || undefined);
      setAiResult(res);
    } catch (err: any) {
      setAiError(err.message || "Failed to process AI search");
    } finally {
      setAiLoading(false);
    }
  };

  // Run AI search automatically if query is present in url when switching to AI mode
  useEffect(() => {
    if (searchMode === "ai" && aiQuery.trim() && !aiResult && !aiLoading) {
      executeAISearch();
    }
  }, [searchMode]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
  };

  const resetFilters = () => {
    setQuery("");
    setCountry("");
    setState("");
    setCity("");
    setInstitutionType("");
    setAdmissionStatus("");
    setDegreeType("");
    setHasScholarship(false);
    setCurrentPage(1);
    router.push("/search");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header with Mode Toggles */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            College Discovery & Intelligence
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Search verified institutional facts with live autocomplete or ask conversational queries via Gemini AI.
          </p>
        </div>

        {/* Mode Toggle Switch */}
        <div className="inline-flex items-center p-1 rounded-2xl bg-slate-100 border border-slate-200">
          <button
            type="button"
            onClick={() => setSearchMode("directory")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
              searchMode === "directory"
                ? "bg-white text-slate-900 shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Building2 className="h-4 w-4 text-blue-600" />
            <span>Directory Search</span>
          </button>

          <button
            type="button"
            onClick={() => setSearchMode("ai")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
              searchMode === "ai"
                ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            <Sparkles className="h-4 w-4" />
            <span>AI Smart Search (Gemini)</span>
          </button>
        </div>
      </div>

      {/* -------------------- AI SMART SEARCH VIEW -------------------- */}
      {searchMode === "ai" && (
        <div className="space-y-8 animate-in fade-in duration-200">
          {/* AI Query Box & API Key Configuration */}
          <div className="bg-gradient-to-br from-blue-50/60 via-white to-indigo-50/40 p-6 sm:p-8 rounded-3xl border border-blue-200/80 shadow-md space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-sm">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">Conversational College Counseling with Gemini</h2>
                  <p className="text-xs text-slate-500">Ask in plain English about courses, entrance cutoffs, budget, scholarships, and placements.</p>
                </div>
              </div>

              {/* Gemini API Key input toggle */}
              <div className="relative flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm max-w-xs">
                <Key className="h-3.5 w-3.5 text-blue-600 flex-shrink-0" />
                <input
                  type={showApiKey ? "text" : "password"}
                  value={geminiApiKey}
                  onChange={(e) => handleApiKeyChange(e.target.value)}
                  placeholder="Custom Gemini Key (Optional)"
                  className="w-full text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none bg-transparent"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="text-slate-400 hover:text-slate-600 transition"
                >
                  {showApiKey ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                </button>
              </div>
            </div>

            {/* AI Search Prompt Form */}
            <form onSubmit={executeAISearch} className="relative flex flex-col sm:flex-row items-center gap-3">
              <div className="relative w-full">
                <Search className="h-5 w-5 text-slate-400 absolute left-4 top-3.5" />
                <input
                  type="text"
                  value={aiQuery}
                  onChange={(e) => setAiQuery(e.target.value)}
                  placeholder="e.g. Colleges in south India offering BTech AI with highest placement packages above 30 LPA and open admissions"
                  className="w-full pl-12 pr-4 py-3.5 text-sm sm:text-base rounded-2xl border border-slate-300/80 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-600 text-slate-900"
                />
              </div>

              <button
                type="submit"
                disabled={aiLoading || !aiQuery.trim()}
                className="w-full sm:w-auto px-7 py-3.5 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-sm shadow-md transition disabled:opacity-50 flex items-center justify-center gap-2 flex-shrink-0"
              >
                {aiLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    <span>Ask Gemini</span>
                  </>
                )}
              </button>
            </form>

            {/* Quick Prompt Suggestions */}
            <div className="flex items-center gap-2 flex-wrap text-xs text-slate-600 pt-1">
              <span className="font-semibold text-slate-400">Try asking:</span>
              {[
                "Best colleges for computer science in Hyderabad with fees",
                "Universities offering international merit scholarships",
                "Top engineering institutes with highest packages above 50 LPA",
                "Colleges currently accepting applications for 2026-27"
              ].map((promptText) => (
                <button
                  key={promptText}
                  type="button"
                  onClick={() => {
                    setAiQuery(promptText);
                  }}
                  className="px-2.5 py-1 rounded-lg bg-white/80 border border-slate-200 hover:border-blue-400 hover:text-blue-600 text-slate-700 transition"
                >
                  &quot;{promptText}&quot;
                </button>
              ))}
            </div>
          </div>

          {/* AI Search Loading State */}
          {aiLoading && (
            <div className="p-16 text-center bg-white rounded-3xl border border-slate-200 shadow-sm space-y-4">
              <Loader2 className="h-10 w-10 text-blue-600 animate-spin mx-auto" />
              <div className="space-y-1">
                <h3 className="text-base font-bold text-slate-900">Gemini is analyzing your educational inquiry</h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  Cross-referencing verified institutional databases, degrees, admission deadlines, and official domains...
                </p>
              </div>
            </div>
          )}

          {/* AI Search Error */}
          {aiError && (
            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 text-xs font-medium flex items-center justify-between">
              <span>{aiError}</span>
              <button
                type="button"
                onClick={() => setAiError(null)}
                className="text-amber-900 underline font-semibold"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* AI Search Response */}
          {aiResult && !aiLoading && (
            <div className="space-y-8 animate-in fade-in duration-300">
              {/* AI Guidance Box */}
              <div className="p-6 sm:p-8 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
                  <Sparkles className="h-4 w-4 text-indigo-600" />
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
                    Gemini Academic Counseling Assessment
                  </span>
                </div>

                <div className="prose prose-sm text-slate-700 leading-relaxed max-w-none whitespace-pre-wrap">
                  {aiResult.ai_answer}
                </div>
              </div>

              {/* Recommended Colleges Cards */}
              {aiResult.recommended_institutions && aiResult.recommended_institutions.length > 0 && (
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                    <Building2 className="h-5 w-5 text-blue-600" />
                    <span>Recommended Institutions for this Inquiry</span>
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {aiResult.recommended_institutions.map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-5 bg-white rounded-2xl border border-slate-200 hover:border-blue-400 hover:shadow-md transition space-y-4 flex flex-col justify-between"
                      >
                        <div className="space-y-2">
                          <div className="flex items-start justify-between gap-2">
                            <h4 className="text-base font-bold text-slate-900 leading-snug">
                              {rec.name}
                            </h4>
                          </div>

                          {rec.location && (
                            <div className="flex items-center gap-1 text-xs text-slate-500">
                              <MapPin className="h-3.5 w-3.5 text-slate-400" />
                              <span>{rec.location}</span>
                            </div>
                          )}

                          {rec.key_highlights && (
                            <div className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                              <strong className="text-slate-800">Highlights:</strong> {rec.key_highlights}
                            </div>
                          )}

                          {rec.why_recommended && (
                            <div className="text-xs text-blue-800 bg-blue-50/60 p-2.5 rounded-xl border border-blue-100">
                              <strong>Why Recommended:</strong> {rec.why_recommended}
                            </div>
                          )}
                        </div>

                        <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
                          {rec.matched_id ? (
                            <Link
                              href={`/colleges/${rec.matched_id}`}
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-blue-600 text-white hover:bg-blue-700 transition"
                            >
                              <span>View Profile</span>
                              <ArrowRight className="h-3.5 w-3.5" />
                            </Link>
                          ) : (
                            <Link
                              href={`/scanner?name=${encodeURIComponent(rec.name)}&url=${encodeURIComponent(rec.official_website || "")}`}
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-900 text-white hover:bg-slate-800 transition"
                            >
                              <Sparkles className="h-3.5 w-3.5 text-blue-400" />
                              <span>Index & Scan</span>
                            </Link>
                          )}

                          {rec.official_website && (
                            <a
                              href={rec.official_website}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-blue-600 transition"
                            >
                              <span>Official Site</span>
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* -------------------- DIRECTORY SEARCH VIEW -------------------- */}
      {searchMode === "directory" && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 animate-in fade-in duration-200">
          {/* Filters Sidebar */}
          <aside className="lg:col-span-1 space-y-6">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2 text-sm font-bold text-slate-900">
                  <SlidersHorizontal className="h-4 w-4 text-blue-600" />
                  <span>Filters</span>
                </div>
                <button
                  type="button"
                  onClick={resetFilters}
                  className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1 transition"
                >
                  <RotateCcw className="h-3 w-3" />
                  <span>Reset</span>
                </button>
              </div>

              {/* Admission Status Filter */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Admission Status
                </label>
                <select
                  value={admissionStatus}
                  onChange={(e) => { setAdmissionStatus(e.target.value); setCurrentPage(1); }}
                  className="w-full text-xs rounded-xl border border-slate-200 bg-slate-50/50 p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="">All Statuses</option>
                  <option value="OPEN">Applications Open</option>
                  <option value="UPCOMING">Upcoming</option>
                  <option value="ONGOING">Ongoing</option>
                  <option value="CLOSED">Closed</option>
                </select>
              </div>

              {/* Institution Type Filter */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Institution Type
                </label>
                <select
                  value={institutionType}
                  onChange={(e) => { setInstitutionType(e.target.value); setCurrentPage(1); }}
                  className="w-full text-xs rounded-xl border border-slate-200 bg-slate-50/50 p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="">All Types</option>
                  <option value="University">University</option>
                  <option value="Institute">Institute of National Importance</option>
                  <option value="College">Autonomous College</option>
                  <option value="Deemed">Deemed University</option>
                </select>
              </div>

              {/* Degree Type Filter */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Degree Level
                </label>
                <select
                  value={degreeType}
                  onChange={(e) => { setDegreeType(e.target.value); setCurrentPage(1); }}
                  className="w-full text-xs rounded-xl border border-slate-200 bg-slate-50/50 p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="">All Degree Levels</option>
                  <option value="Undergraduate">Undergraduate (BTech, BSc, BBA)</option>
                  <option value="Postgraduate">Postgraduate (MTech, MSc, MBA)</option>
                  <option value="Doctoral">Doctoral (PhD)</option>
                  <option value="Integrated">Dual Degree / Integrated</option>
                </select>
              </div>

              {/* City Filter */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  City
                </label>
                <input
                  type="text"
                  placeholder="e.g. Mumbai, Hyderabad, Bengaluru"
                  value={city}
                  onChange={(e) => { setCity(e.target.value); setCurrentPage(1); }}
                  className="w-full text-xs rounded-xl border border-slate-200 bg-slate-50/50 p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              {/* State Filter */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  State
                </label>
                <input
                  type="text"
                  placeholder="e.g. Maharashtra, Telangana"
                  value={state}
                  onChange={(e) => { setState(e.target.value); setCurrentPage(1); }}
                  className="w-full text-xs rounded-xl border border-slate-200 bg-slate-50/50 p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              {/* Scholarships Toggle */}
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs font-medium text-slate-700">Has Scholarships</span>
                <input
                  type="checkbox"
                  checked={hasScholarship}
                  onChange={(e) => { setHasScholarship(e.target.checked); setCurrentPage(1); }}
                  className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                />
              </div>
            </div>
          </aside>

          {/* Results Area */}
          <div className="lg:col-span-3 space-y-6">
            {/* Search Bar with Live Auto-Suggest Dropdown */}
            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
              <form onSubmit={handleSearchSubmit} className="relative w-full sm:max-w-md">
                <CollegeSearchAutocomplete
                  value={query}
                  onChange={(val) => {
                    setQuery(val);
                    setCurrentPage(1);
                  }}
                  autoNavigate={false}
                  placeholder="Type college name (auto-suggest active)..."
                  inputClassName="py-2 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50/50 focus:ring-2 focus:ring-blue-600"
                />
              </form>

              <div className="text-xs text-slate-500 font-medium">
                Showing <span className="font-bold text-slate-900">{results.length}</span> of <span className="font-bold text-slate-900">{totalCount}</span> verified institutions
              </div>
            </div>

            {/* Cards Grid */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i} className="h-72 rounded-2xl bg-slate-100 animate-pulse border border-slate-200" />
                ))}
              </div>
            ) : results.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.map((col) => (
                  <CollegeCard key={col.id} college={col} />
                ))}
              </div>
            ) : (
              <div className="p-16 text-center bg-white rounded-2xl border border-slate-200 space-y-3">
                <Building2 className="h-12 w-12 text-slate-300 mx-auto" />
                <h3 className="text-base font-bold text-slate-800">No institutions match your search criteria</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Try adjusting your filters, ask Gemini via AI Smart Search, or use the Website Scanner to crawl and index a new institutional portal.
                </p>
                <div className="flex items-center justify-center gap-3 pt-2">
                  <button
                    type="button"
                    onClick={resetFilters}
                    className="px-4 py-2 text-xs font-semibold bg-blue-50 text-blue-700 rounded-xl hover:bg-blue-100 transition"
                  >
                    Reset All Filters
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setSearchMode("ai");
                      setAiQuery(query || "Top colleges in India");
                    }}
                    className="px-4 py-2 text-xs font-semibold bg-indigo-50 text-indigo-700 rounded-xl hover:bg-indigo-100 transition inline-flex items-center gap-1.5"
                  >
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Ask Gemini AI</span>
                  </button>
                </div>
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 pt-4">
                <button
                  type="button"
                  disabled={currentPage <= 1}
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  className="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 transition"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <span className="text-xs font-semibold text-slate-700 px-3">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  type="button"
                  disabled={currentPage >= totalPages}
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  className="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 transition"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-sm text-slate-500">Loading discovery directory...</div>}>
      <SearchContent />
    </Suspense>
  );
}
