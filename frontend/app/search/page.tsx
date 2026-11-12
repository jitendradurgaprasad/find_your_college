"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { 
  Search, 
  Filter, 
  RotateCcw, 
  SlidersHorizontal, 
  Building2, 
  MapPin, 
  ChevronLeft, 
  ChevronRight,
  GraduationCap
} from "lucide-react";
import CollegeCard from "@/components/CollegeCard";
import { fetchUniversities, UniversitySummary } from "@/lib/api";

function SearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

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

  // Sync state when URL params change
  useEffect(() => {
    setQuery(searchParams.get("query") || "");
    setCountry(searchParams.get("country") || "");
    setState(searchParams.get("state") || "");
    setCity(searchParams.get("city") || "");
    setInstitutionType(searchParams.get("institution_type") || "");
    setAdmissionStatus(searchParams.get("admission_status") || "");
    setDegreeType(searchParams.get("degree_type") || "");
    setHasScholarship(searchParams.get("has_scholarship") === "true");
  }, [searchParams]);

  // Execute Search
  useEffect(() => {
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
  }, [query, country, state, city, institutionType, admissionStatus, degreeType, hasScholarship, currentPage]);

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
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          College Discovery Directory
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Explore and filter verified institutions indexed from official educational web sources.
        </p>
      </div>

      {/* Main Search and Filter Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
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
                <option value="OPEN">Open Admissions</option>
                <option value="ONGOING">Ongoing Counselling</option>
                <option value="UPCOMING">Upcoming Cycles</option>
                <option value="CLOSED">Closed Applications</option>
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
                <option value="">All Institution Types</option>
                <option value="National Importance">Institute of National Importance</option>
                <option value="Deemed">Deemed University</option>
                <option value="University">State / Central University</option>
                <option value="College">Autonomous College</option>
              </select>
            </div>

            {/* Degree / Program Level Filter */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Degree Level
              </label>
              <select
                value={degreeType}
                onChange={(e) => { setDegreeType(e.target.value); setCurrentPage(1); }}
                className="w-full text-xs rounded-xl border border-slate-200 bg-slate-50/50 p-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                <option value="">All Degrees</option>
                <option value="Undergraduate">Undergraduate (B.Tech, B.Sc, BBA)</option>
                <option value="Postgraduate">Postgraduate (M.Tech, MBA, M.Sc)</option>
                <option value="PhD">Doctoral / Ph.D.</option>
              </select>
            </div>

            {/* City Filter */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                City / Region
              </label>
              <input
                type="text"
                placeholder="e.g. Mumbai, Hyderabad, Pilani"
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
          {/* Search Bar & Result Counter */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
            <form onSubmit={handleSearchSubmit} className="relative w-full sm:max-w-md">
              <Search className="h-4 w-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Search by college name, specialization..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50/50 focus:outline-none focus:ring-2 focus:ring-blue-600"
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
                Try adjusting your filters or use the Website Scanner to crawl and index a new institutional portal.
              </p>
              <button
                type="button"
                onClick={resetFilters}
                className="px-4 py-2 text-xs font-semibold bg-blue-50 text-blue-700 rounded-xl hover:bg-blue-100 transition"
              >
                Reset All Filters
              </button>
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
