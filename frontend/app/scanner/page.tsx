"use client";

import { useState, useEffect } from "react";
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
  FileText
} from "lucide-react";
import { startCrawlJob, fetchCrawlStatus, CrawlJobStatus } from "@/lib/api";

export default function WebsiteScannerPage() {
  const [url, setUrl] = useState("");
  const [universityName, setUniversityName] = useState("");
  const [maxDepth, setMaxDepth] = useState(2);
  const [maxPages, setMaxPages] = useState(25);

  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<CrawlJobStatus | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

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

  const handleStartScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    const cleanUrl = url.trim();
    if (!cleanUrl.startsWith("http://") && !cleanUrl.startsWith("https://")) {
      setErrorMsg("Please provide a valid URL with http:// or https://");
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
          Enter any accredited university or college website URL to discover pages, extract course catalogues, admission statuses, faculty directories, and placement reports with real-time audit logging.
        </p>
      </div>

      {/* URL Entry Form */}
      <div className="p-6 sm:p-8 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-6">
        <form onSubmit={handleStartScan} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2 space-y-1.5">
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
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={isScanning}
                  className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-slate-200 bg-slate-50/50 focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Institution Name (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. IIT Bombay"
                value={universityName}
                onChange={(e) => setUniversityName(e.target.value)}
                disabled={isScanning}
                className="w-full px-4 py-2.5 text-sm rounded-xl border border-slate-200 bg-slate-50/50 focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50"
              />
            </div>
          </div>

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
              <span>SSRF protected • Respects robots.txt policies</span>
            </div>

            <button
              type="submit"
              disabled={isScanning}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-sm transition active:scale-95 disabled:opacity-50"
            >
              {isScanning ? (
                <>
                  <RotateCw className="h-4 w-4 animate-spin" />
                  <span>Crawling Website...</span>
                </>
              ) : (
                <>
                  <Cpu className="h-4 w-4" />
                  <span>Start Autonomous Scan</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* SCAN PROGRESS & METRICS CONSOLE */}
      {jobStatus && (
        <div className="p-6 sm:p-8 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${
                  jobStatus.status === "COMPLETED" ? "bg-emerald-500" :
                  jobStatus.status === "RUNNING" ? "bg-blue-500 animate-ping" : "bg-rose-500"
                }`} />
                <h3 className="text-base font-bold text-slate-900">
                  Crawl Status: <span className="uppercase text-blue-600">{jobStatus.status}</span>
                </h3>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Seed Target: <strong className="text-slate-700">{jobStatus.seed_url}</strong>
              </p>
            </div>

            {jobStatus.status === "COMPLETED" && jobStatus.university_id && (
              <Link
                href={`/colleges/${jobStatus.university_id}`}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition shadow-sm"
              >
                <span>Open Extracted Profile</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            )}
          </div>

          {/* Real Backend Progress Bar */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
              <span>Pages Scanned: {jobStatus.pages_crawled} / {jobStatus.max_pages}</span>
              <span>{calculateProgressPercent()}%</span>
            </div>
            <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
              <div
                className={`h-full transition-all duration-300 ${
                  jobStatus.status === "COMPLETED" ? "bg-emerald-500" : "bg-blue-600"
                }`}
                style={{ width: `${calculateProgressPercent()}%` }}
              />
            </div>
          </div>

          {/* Real Live Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-xs text-slate-500 font-medium">Discovered Links</span>
              <p className="text-xl font-extrabold text-slate-900 mt-0.5">{jobStatus.pages_discovered}</p>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-xs text-slate-500 font-medium">Crawled Pages</span>
              <p className="text-xl font-extrabold text-blue-600 mt-0.5">{jobStatus.pages_crawled}</p>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-xs text-slate-500 font-medium">Records Extracted</span>
              <p className="text-xl font-extrabold text-emerald-600 mt-0.5">{jobStatus.records_extracted}</p>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-xs text-slate-500 font-medium">Scan Duration</span>
              <p className="text-xl font-extrabold text-slate-900 mt-0.5">
                {jobStatus.duration_seconds ? `${jobStatus.duration_seconds}s` : "In Progress"}
              </p>
            </div>
          </div>

          {/* Live Extraction Terminal Console */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-700 uppercase tracking-wider">
              <Terminal className="h-4 w-4 text-slate-500" />
              <span>Real-Time Engine Console Logs</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-950 font-mono text-xs text-slate-300 max-h-60 overflow-y-auto space-y-1.5 shadow-inner">
              {jobStatus.logs && jobStatus.logs.length > 0 ? (
                jobStatus.logs.map((log, lIdx) => (
                  <div key={lIdx} className="flex items-start gap-2 leading-relaxed">
                    <span className="text-slate-600 select-none">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                    <span className={`font-bold select-none ${
                      log.level === "SUCCESS" ? "text-emerald-400" :
                      log.level === "ERROR" ? "text-rose-400" :
                      log.level === "WARNING" ? "text-amber-400" : "text-blue-400"
                    }`}>
                      [{log.level}]
                    </span>
                    <span className="text-slate-200">{log.message}</span>
                  </div>
                ))
              ) : (
                <div className="text-slate-500 italic">Initializing crawler worker engine...</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
