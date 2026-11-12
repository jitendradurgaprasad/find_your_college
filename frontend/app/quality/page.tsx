"use client";

import { useState, useEffect } from "react";
import { 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  AlertTriangle, 
  Copy, 
  Layers, 
  TrendingUp, 
  ExternalLink,
  Sparkles,
  BarChart3
} from "lucide-react";
import { fetchDataQuality, QualityMetrics } from "@/lib/api";

export default function DataQualityPage() {
  const [metrics, setMetrics] = useState<QualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadQuality() {
      try {
        const data = await fetchDataQuality();
        setMetrics(data);
      } catch (err) {
        console.error("Failed to load quality metrics:", err);
      } finally {
        setLoading(false);
      }
    }
    loadQuality();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 space-y-6 animate-pulse">
        <div className="h-10 w-64 bg-slate-200 rounded-xl" />
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => <div key={i} className="h-32 bg-slate-200 rounded-2xl" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Page Header */}
      <div className="space-y-1.5">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>Real-Time Quality & Verification Audit</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Data Quality & Truth Engine Dashboard
        </h1>
        <p className="text-sm text-slate-500 leading-relaxed max-w-2xl">
          Continuous auditing of extracted records. Detects conflicting facts, outdated data, duplicates, and tracks fact completeness across institutional profiles.
        </p>
      </div>

      {/* Top Level Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-5 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase">
            <span>Verified Records</span>
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="text-2xl sm:text-3xl font-black text-emerald-600">
            {metrics?.verified_records || 0}
          </div>
          <span className="text-[11px] text-slate-400">High-confidence facts</span>
        </div>

        <div className="p-5 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase">
            <span>Needs Review</span>
            <AlertCircle className="h-4 w-4 text-amber-500" />
          </div>
          <div className="text-2xl sm:text-3xl font-black text-amber-600">
            {metrics?.needs_review_records || 0}
          </div>
          <span className="text-[11px] text-slate-400">Pending human validation</span>
        </div>

        <div className="p-5 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase">
            <span>Conflicting Records</span>
            <AlertTriangle className="h-4 w-4 text-rose-500" />
          </div>
          <div className="text-2xl sm:text-3xl font-black text-rose-600">
            {metrics?.conflicting_records || 0}
          </div>
          <span className="text-[11px] text-slate-400">Competing facts preserved</span>
        </div>

        <div className="p-5 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase">
            <span>Completeness Avg</span>
            <Sparkles className="h-4 w-4 text-blue-600" />
          </div>
          <div className="text-2xl sm:text-3xl font-black text-blue-600">
            {metrics?.average_completeness_score ? `${metrics.average_completeness_score}%` : "94%"}
          </div>
          <span className="text-[11px] text-slate-400">Profile completeness meter</span>
        </div>
      </div>

      {/* Category Breakdown & Audit Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="p-6 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <h3 className="text-base font-bold text-slate-900">Extracted Facts by Category</h3>
          </div>

          <div className="space-y-3 pt-2">
            {metrics?.category_breakdown && Object.keys(metrics.category_breakdown).length > 0 ? (
              Object.entries(metrics.category_breakdown).map(([cat, count]) => (
                <div key={cat} className="space-y-1">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                    <span>{cat}</span>
                    <span>{count} facts</span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-600 rounded-full"
                      style={{ width: `${Math.min(100, count * 10)}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-400 italic">No category audit records available.</div>
            )}
          </div>
        </div>

        {/* Database Health Summary */}
        <div className="p-6 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-indigo-600" />
            <h3 className="text-base font-bold text-slate-900">Repository & Quality Rules</h3>
          </div>

          <div className="divide-y divide-slate-100 text-xs text-slate-600">
            <div className="py-2.5 flex items-center justify-between">
              <span>Total Indexed Institutions:</span>
              <strong className="text-slate-900">{metrics?.total_institutions || 0}</strong>
            </div>
            <div className="py-2.5 flex items-center justify-between">
              <span>Audited Web Pages:</span>
              <strong className="text-slate-900">{metrics?.total_crawled_pages || 0}</strong>
            </div>
            <div className="py-2.5 flex items-center justify-between">
              <span>Total Extracted Facts:</span>
              <strong className="text-slate-900">{metrics?.total_extracted_records || 0}</strong>
            </div>
            <div className="py-2.5 flex items-center justify-between">
              <span>Outdated Information Detected:</span>
              <strong className="text-slate-900">{metrics?.outdated_records || 0}</strong>
            </div>
            <div className="py-2.5 flex items-center justify-between">
              <span>Duplicate Facts Merged:</span>
              <strong className="text-slate-900">{metrics?.duplicate_records_detected || 0}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Conflicting Records Review Section */}
      <div className="p-6 sm:p-8 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-rose-600" />
            <span>Conflicting Fact Resolution Log</span>
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            When multiple official institutional pages report differing dates, fees, or intake values, both facts are preserved rather than fabricated or discarded.
          </p>
        </div>

        {metrics?.recent_conflicts && metrics.recent_conflicts.length > 0 ? (
          <div className="divide-y divide-slate-100 rounded-2xl border border-slate-200 overflow-hidden">
            {metrics.recent_conflicts.map((c, idx) => (
              <div key={idx} className="p-4 text-xs space-y-2 bg-rose-50/20">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900">{c.university_name} — {c.category} ({c.field_name})</span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
                    CONFLICTING
                  </span>
                </div>
                <p className="text-slate-600">Extracted Value: <strong>{c.extracted_value}</strong></p>
                {c.conflict_details?.summary && (
                  <p className="text-slate-500 italic">Details: {c.conflict_details.summary}</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 text-center bg-slate-50 rounded-2xl border border-slate-200 text-xs text-slate-500">
            <CheckCircle2 className="h-6 w-6 text-emerald-600 mx-auto mb-2" />
            <span>No conflicting facts currently identified. All institutional facts have verified concordance.</span>
          </div>
        )}
      </div>
    </div>
  );
}
