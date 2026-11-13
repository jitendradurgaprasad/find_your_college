"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { 
  Cpu, 
  Globe, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  RotateCw, 
  Terminal, 
  ExternalLink, 
  ArrowRight,
  Layers,
  FileCheck,
  FileText,
  Sparkles,
  Loader2,
  Key
} from "lucide-react";
import CollegeSearchAutocomplete from "@/components/CollegeSearchAutocomplete";
import { startCrawlJob, fetchCrawlStatus, resolveCollegeUrl, CrawlJobStatus, CollegeSuggestion } from "@/lib/api";

function ScannerContent() {
  const searchParams = useSearchParams();

  const [url, setUrl] = useState(searchParams.get("url") || "");
  const [universityName, setUniversityName] = useState(searchParams.get("name") || "");
  const [maxDepth, setMaxDepth] = useState(2);
  const [maxPages, setMaxPages] = useState(25);

  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<CrawlJobStatus | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Auto URL fetching state
  const [isResolvingUrl, setIsResolvingUrl] = useState(false);
  const [resolveSuccessNote, setResolveSuccessNote] = useState<string | null>(null);
  const [geminiApiKey, setGeminiApiKey] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined") {
      setGeminiApiKey(localStorage.getItem("FIND_YOUR_COLLEGE_GEMINI_KEY") || "");
    }
  }, []);

  // Update when URL query params change
  useEffect(() => {
    const qUrl = searchParams.get("url");
    const qName = searchParams.get("name");
    if (qUrl) setUrl(qUrl);
    if (qName) setUniversityName(qName);
  }, [searchParams]);

  // Pre-flight: wake up Render backend on page load (free tier cold-start)
  const [backendReady, setBackendReady] = useState(false);
  useEffect(() => {
    fetch((process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/api").replace("/api", "/health"))
      .then((res) => { if (res.ok) setBackendReady(true); })
      .catch(() => {});
  }, []);

  // Real-time status polling
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (activeJobId && isScanning) {
      interval = setInterval(async () => {
        const data = await fetchCrawlStatus(activeJobId);
        if (data) {
          setJobStatus(data);
          if (data.status === "COMPLETED" || data.status === "FAILED") {
            setIsScanning(false);
          }
        }
      }, 1500);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [activeJobId, isScanning]);

  // Auto URL fetching by college name
  const handleAutoFetchUrl = async (nameToFetch?: string) => {
    const targetName = nameToFetch || universityName;
    if (!targetName.trim()) {
      setErrorMsg("Please type a college name first to auto-fetch its official URL.");
      return;
    }

    setIsResolvingUrl(true);
    setErrorMsg(null);
    setResolveSuccessNote(null);

    try {
      const res = await resolveCollegeUrl(targetName, geminiApiKey || undefined);
      if (res.official_website) {
        setUrl(res.official_website);
        setResolveSuccessNote(
          `Official URL fetched: ${res.domain} (${res.source}) - ${res.is_accessible ? "Accessible & Verified" : "Identified"}`
        );
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Could not automatically resolve official website.");
    } finally {
      setIsResolvingUrl(false);
    }
  };

  const handleSelectCollegeSuggestion = (college: CollegeSuggestion) => {
    setUniversityName(college.name);
    if (college.official_website) {
      setUrl(college.official_website);
      setResolveSuccessNote(`Official URL auto-filled from directory: ${college.official_website}`);
    } else {
      handleAutoFetchUrl(college.name);
    }
  };

  const handleStartScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    const cleanUrl = url.trim();
    if (!cleanUrl.startsWith("http://") && !cleanUrl.startsWith("https://")) {
      setErrorMsg("Please provide a valid URL starting with http:// or https://");
      return;
    }

    try {
      setIsScanning(true);
      const res = await startCrawlJob(cleanUrl, maxDepth, maxPages, universityName.trim() || undefined);
      setActiveJobId(res.job_id);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to start crawler engine");
      setIsScanning(false);
    }
  };

  const calculateProgressPercent = () => {
    if (!jobStatus || jobStatus.max_pages === 0) return 0;
    if (jobStatus.status === "COMPLETED") return 100;
    const pct = Math.round(((jobStatus.pages_crawled || 0) / jobStatus.max_pages) * 100);
    return Math.min(pct, 95);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Page Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
          <Cpu className="h-3.5 w-3.5" />
          <span>Autonomous Scraping & Verification System</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Institutional Website Scanner
        </h1>
        <p className="text-sm text-slate-500 leading-relaxed max-w-2xl">
          Enter any college name to auto-discover its official institutional website or paste an official domain to crawl course catalogues, admission statuses, faculty directories, and placement reports.
        </p>
      </div>

      {/* URL Entry Form */}
      <div className="p-6 sm:p-8 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-6">
        <form onSubmit={handleStartScan} className="space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Auto-suggesting College Name Input */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  College / University Name
                </label>
                <button
                  type="button"
                  onClick={() => handleAutoFetchUrl()}
                  disabled={isResolvingUrl || !universityName.trim()}
                  className="text-xs text-blue-600 hover:text-blue-800 font-bold inline-flex items-center gap-1 disabled:opacity-40 transition"
                >
                  {isResolvingUrl ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
                  <span>Auto-Fetch URL</span>
                </button>
              </div>

              <CollegeSearchAutocomplete
                value={universityName}
                onChange={setUniversityName}
                onSelect={handleSelectCollegeSuggestion}
                autoNavigate={false}
                placeholder="Type college name (e.g. NIT Warangal, IIT Delhi)..."
                inputClassName="py-2.5 text-sm rounded-xl border border-slate-200 bg-slate-50/50 focus:ring-2 focus:ring-blue-600"
              />
            </div>

            {/* Official Website URL */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Official Website URL
              </label>
              <div className="relative">
                <Globe className="h-4 w-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="url"
                  required
                  placeholder="https://www.iitb.ac.in"
                  value={url}
                  onChange={(e) => {
                    setUrl(e.target.value);
                    setResolveSuccessNote(null);
                  }}
                  disabled={isScanning}
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-slate-200 bg-slate-50/50 focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50"
                />
              </div>
            </div>
          </div>

          {/* Resolve Success Note */}
          {resolveSuccessNote && (
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-medium flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0" />
              <span>{resolveSuccessNote}</span>
            </div>
          )}

          {/* Advanced Crawler Controls */}
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="space-y-1">
              <span className="text-xs font-medium text-slate-600">Max Depth: <strong>{maxDepth}</strong></span>
              <input
                type="range"
                min="1"
                max="3"
                value={maxDepth}
                onChange={(e) => setMaxDepth(parseInt(e.target.value))}
                disabled={isScanning}
                className="w-full accent-blue-600"
              />
            </div>

            <div className="space-y-1">
              <span className="text-xs font-medium text-slate-600">Max Pages: <strong>{maxPages}</strong></span>
              <input
                type="range"
                min="10"
                max="50"
                step="5"
                value={maxPages}
                onChange={(e) => setMaxPages(parseInt(e.target.value))}
                disabled={isScanning}
                className="w-full accent-blue-600"
              />
            </div>
          </div>

          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <div className="pt-2 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <ShieldCheck className="h-4 w-4 text-emerald-600" />
              <span>SSRF protected & robots.txt compliant</span>
            </div>

            <button
              type="submit"
              disabled={isScanning || !url.trim()}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 text-white font-bold text-sm hover:bg-blue-700 disabled:opacity-50 transition shadow-sm"
            >
              {isScanning ? (
                <>
                  <RotateCw className="h-4 w-4 animate-spin" />
                  <span>Crawling in Progress...</span>
                </>
              ) : (
                <>
                  <span>Start Autonomous Scan</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Real-time Status Card */}
      {jobStatus && (
        <div className="p-6 sm:p-8 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Scan Job</span>
                <span className="text-xs font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-600">{jobStatus.job_id.substring(0, 8)}...</span>
              </div>
              <h3 className="text-base font-bold text-slate-900">{jobStatus.seed_url}</h3>
            </div>

            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
              jobStatus.status === "COMPLETED" ? "bg-emerald-100 text-emerald-800" :
              jobStatus.status === "RUNNING" ? "bg-blue-100 text-blue-800 animate-pulse" :
              jobStatus.status === "FAILED" ? "bg-rose-100 text-rose-800" : "bg-slate-100 text-slate-800"
            }`}>
              {jobStatus.status}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold text-slate-600">
              <span>Overall Progress</span>
              <span>{calculateProgressPercent()}%</span>
            </div>
            <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-blue-600 transition-all duration-300 rounded-full"
                style={{ width: `${calculateProgressPercent()}%` }}
              />
            </div>
          </div>

          {/* Real-time Live Counters */}
          <div className="grid grid-cols-3 gap-4 pt-2">
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 text-center">
              <div className="text-2xl font-extrabold text-slate-900">{jobStatus.pages_discovered}</div>
              <div className="text-xs font-medium text-slate-500 mt-1 flex items-center justify-center gap-1">
                <Globe className="h-3.5 w-3.5 text-blue-500" />
                <span>Pages Discovered</span>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 text-center">
              <div className="text-2xl font-extrabold text-slate-900">{jobStatus.pages_crawled}</div>
              <div className="text-xs font-medium text-slate-500 mt-1 flex items-center justify-center gap-1">
                <Layers className="h-3.5 w-3.5 text-indigo-500" />
                <span>Pages Crawled</span>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 text-center">
              <div className="text-2xl font-extrabold text-slate-900">{jobStatus.records_extracted}</div>
              <div className="text-xs font-medium text-slate-500 mt-1 flex items-center justify-center gap-1">
                <FileCheck className="h-3.5 w-3.5 text-emerald-500" />
                <span>Facts Extracted</span>
              </div>
            </div>
          </div>

          {/* Real-time Live Log Feed */}
          {jobStatus.logs && jobStatus.logs.length > 0 && (
            <div className="space-y-2 pt-2">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
                <Terminal className="h-3.5 w-3.5 text-slate-400" />
                <span>Live Crawler Activity</span>
              </div>
              <div className="bg-slate-950 rounded-2xl p-4 font-mono text-xs text-slate-300 max-h-48 overflow-y-auto space-y-1.5 shadow-inner">
                {jobStatus.logs.map((log: any, idx: number) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-slate-500 select-none">[{log.level}]</span>
                    <span className={
                      log.level === "ERROR" ? "text-rose-400" :
                      log.level === "WARNING" ? "text-amber-400" : "text-slate-300"
                    }>
                      {log.message}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action When Completed */}
          {jobStatus.status === "COMPLETED" && (
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                <span className="text-sm font-bold text-emerald-900">
                  Crawl & Extraction Completed! Verified facts added to database.
                </span>
              </div>
              <Link
                href="/search"
                className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-bold text-xs hover:bg-emerald-700 transition"
              >
                View in Directory
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function WebsiteScannerPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-sm text-slate-500">Loading website scanner...</div>}>
      <ScannerContent />
    </Suspense>
  );
}
