"use client";

import { useState, useEffect } from "react";
import { Activity, Clock, ShieldCheck, ArrowRight, ExternalLink, RefreshCw } from "lucide-react";
import { fetchMonitoringChanges } from "@/lib/api";

export default function MonitoringPage() {
  const [changes, setChanges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadChanges() {
      try {
        const data = await fetchMonitoringChanges();
        setChanges(data || []);
      } catch (err) {
        console.error("Failed to load monitoring changes:", err);
      } finally {
        setLoading(false);
      }
    }
    loadChanges();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-1.5">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
          <Activity className="h-3.5 w-3.5" />
          <span>Continuous Website Monitoring & Change Detection</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Institutional Change Audit Feed
        </h1>
        <p className="text-sm text-slate-500 leading-relaxed max-w-2xl">
          Tracks updates published across institutional websites. Detects newly opened admissions, changed tuition schedules, newly introduced courses, and updated placement figures.
        </p>
      </div>

      {/* Changes Timeline */}
      {loading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => <div key={i} className="h-24 bg-slate-100 rounded-2xl" />)}
        </div>
      ) : changes.length > 0 ? (
        <div className="divide-y divide-slate-100 rounded-3xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          {changes.map((ch, idx) => (
            <div key={idx} className="p-5 space-y-2 hover:bg-slate-50/50 transition">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    ch.change_type === "MODIFIED" ? "bg-amber-100 text-amber-800" :
                    ch.change_type === "NEW" ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
                  }`}>
                    {ch.change_type}
                  </span>
                  <span className="text-xs font-bold text-slate-900">{ch.university_name}</span>
                  <span className="text-xs text-slate-400">•</span>
                  <span className="text-xs text-blue-600 font-semibold">{ch.category} / {ch.field_name}</span>
                </div>

                <div className="flex items-center gap-2 text-[11px] text-slate-400">
                  <Clock className="h-3 w-3" />
                  <span>{new Date(ch.detected_at).toLocaleDateString()}</span>
                  {ch.source_url && (
                    <a href={ch.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-0.5">
                      <span>Source</span>
                      <ExternalLink className="h-2.5 w-2.5" />
                    </a>
                  )}
                </div>
              </div>

              {/* Value diff */}
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1">
                {ch.previous_value && (
                  <div className="text-rose-700 line-through">
                    <strong className="text-slate-500 font-normal">Previous Value: </strong>{ch.previous_value}
                  </div>
                )}
                <div className="text-slate-900 font-medium">
                  <strong className="text-slate-500 font-normal">Current Value: </strong>{ch.current_value}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-16 text-center bg-white rounded-3xl border border-slate-200 space-y-3">
          <Activity className="h-12 w-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">Monitoring Engine Initialized</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Periodic re-scans are scheduled. When institutional pages change, detailed diffs will appear here automatically.
          </p>
        </div>
      )}
    </div>
  );
}
