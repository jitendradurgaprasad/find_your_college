"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Bookmark, Building2, Trash2, ArrowRight, Scale, ExternalLink } from "lucide-react";
import { fetchUniversities, UniversitySummary } from "@/lib/api";

export default function SavedCollegesPage() {
  const [savedColleges, setSavedColleges] = useState<UniversitySummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSaved() {
      try {
        const data = await fetchUniversities({ page_size: 10 });
        if (data && data.results) {
          // Demo saved items
          setSavedColleges(data.results.slice(0, 3));
        }
      } catch (err) {
        console.error("Failed to load saved colleges:", err);
      } finally {
        setLoading(false);
      }
    }
    loadSaved();
  }, []);

  const handleRemove = (id: string) => {
    setSavedColleges((prev) => prev.filter((item) => item.id !== id));
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <Bookmark className="h-3.5 w-3.5" />
            <span>Personal Watchlist</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-1.5">
            Saved Colleges & Watchlist
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Keep track of admission schedules, placement reports, and scholarship deadlines for your target colleges.
          </p>
        </div>

        {savedColleges.length >= 2 && (
          <Link
            href="/compare"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition"
          >
            <Scale className="h-4 w-4" />
            <span>Compare Saved Colleges</span>
          </Link>
        )}
      </div>

      {loading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((i) => <div key={i} className="h-28 bg-slate-100 rounded-2xl" />)}
        </div>
      ) : savedColleges.length > 0 ? (
        <div className="divide-y divide-slate-200 rounded-3xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          {savedColleges.map((col) => (
            <div key={col.id} className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/50 transition">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                    {col.institution_type}
                  </span>
                  <span className="text-xs font-semibold text-emerald-600">
                    {col.admission_status || "UNKNOWN"}
                  </span>
                </div>
                <h3 className="text-base font-bold text-slate-900">{col.name}</h3>
                <p className="text-xs text-slate-500">{col.city ? `${col.city}, ` : ""}{col.state || col.country}</p>
              </div>

              <div className="flex items-center gap-3">
                <a
                  href={col.official_website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 rounded-xl border border-slate-200 bg-white text-xs text-slate-600 hover:text-blue-600 font-medium flex items-center gap-1 transition"
                >
                  <span>Website</span>
                  <ExternalLink className="h-3 w-3" />
                </a>

                <Link
                  href={`/colleges/${col.slug || col.id}`}
                  className="px-4 py-1.5 rounded-xl bg-blue-50 text-blue-700 hover:bg-blue-100 text-xs font-semibold transition flex items-center gap-1"
                >
                  <span>Explore</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>

                <button
                  type="button"
                  onClick={() => handleRemove(col.id)}
                  className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition"
                  title="Remove"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-16 text-center bg-white rounded-3xl border border-slate-200 space-y-3">
          <Bookmark className="h-12 w-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">Your watchlist is currently empty</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Discover institutions in the search directory and bookmark them to monitor deadlines.
          </p>
          <Link
            href="/search"
            className="inline-block px-4 py-2 text-xs font-semibold bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition"
          >
            Explore Colleges
          </Link>
        </div>
      )}
    </div>
  );
}
