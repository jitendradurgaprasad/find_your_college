"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Settings, 
  Cpu, 
  Database, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  RotateCw, 
  Activity,
  Layers,
  ArrowRight
} from "lucide-react";
import { fetchAdminStats } from "@/lib/api";

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await fetchAdminStats();
        setStats(data);
      } catch (err) {
        console.error("Failed to load admin stats:", err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Page Header */}
      <div className="space-y-1.5">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
          <Settings className="h-3.5 w-3.5 text-slate-500" />
          <span>Operational Control Center</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Administrative & Crawler Operations
        </h1>
        <p className="text-sm text-slate-500 leading-relaxed max-w-2xl">
          Manage background crawl queues, inspect extraction worker health, database storage stats, and search provider connections.
        </p>
      </div>

      {/* Worker Health & System Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase">
            <span>Background Worker</span>
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="text-xl font-bold text-slate-900">
            {stats?.worker_health || "HEALTHY"}
          </div>
          <p className="text-xs text-slate-500">Autonomous thread pool queue active</p>
        </div>

        <div className="p-5 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase">
            <span>Search Discovery</span>
            <Activity className="h-4 w-4 text-blue-600" />
          </div>
          <div className="text-xl font-bold text-slate-900 uppercase">
            {stats?.search_provider || "Tavily / Fallback"}
          </div>
          <p className="text-xs text-slate-500">
            {stats?.search_provider_configured ? "API Key Connected" : "Direct Seed Mode Active"}
          </p>
        </div>

        <div className="p-5 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase">
            <span>Primary Database</span>
            <Database className="h-4 w-4 text-indigo-600" />
          </div>
          <div className="text-xl font-bold text-slate-900">
            {stats?.database?.type || "Supabase PostgreSQL / SQLite"}
          </div>
          <p className="text-xs text-slate-500">19 Normalized Relational Tables</p>
        </div>
      </div>

      {/* Crawl Jobs Status Breakdown */}
      <div className="p-6 sm:p-8 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-5">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Cpu className="h-5 w-5 text-blue-600" />
            <span>Crawl Job Queue Metrics</span>
          </h3>
          <Link
            href="/scanner"
            className="text-xs font-semibold text-blue-600 hover:underline flex items-center gap-1"
          >
            <span>Launch New Scan</span>
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
            <span className="text-xs text-slate-500 font-medium">Total Jobs</span>
            <p className="text-2xl font-extrabold text-slate-900 mt-1">{stats?.jobs?.total || 0}</p>
          </div>
          <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200">
            <span className="text-xs text-blue-700 font-medium">Running Jobs</span>
            <p className="text-2xl font-extrabold text-blue-900 mt-1">{stats?.jobs?.running || 0}</p>
          </div>
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200">
            <span className="text-xs text-emerald-700 font-medium">Completed Jobs</span>
            <p className="text-2xl font-extrabold text-emerald-900 mt-1">{stats?.jobs?.completed || 0}</p>
          </div>
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200">
            <span className="text-xs text-rose-700 font-medium">Failed Jobs</span>
            <p className="text-2xl font-extrabold text-rose-900 mt-1">{stats?.jobs?.failed || 0}</p>
          </div>
        </div>
      </div>

      {/* Database Statistics */}
      <div className="p-6 sm:p-8 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Layers className="h-5 w-5 text-indigo-600" />
          <span>Storage & Entity Statistics</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
            <span className="text-slate-500 font-medium">Institutions Persisted:</span>
            <p className="text-lg font-bold text-slate-900 mt-1">{stats?.database?.universities_count || 0}</p>
          </div>
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
            <span className="text-slate-500 font-medium">Crawled Pages Cached:</span>
            <p className="text-lg font-bold text-slate-900 mt-1">{stats?.database?.crawled_pages_count || 0}</p>
          </div>
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
            <span className="text-slate-500 font-medium">Traceable Extracted Facts:</span>
            <p className="text-lg font-bold text-slate-900 mt-1">{stats?.database?.extracted_records_count || 0}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
