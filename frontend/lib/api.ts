const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/api";

export interface UniversitySummary {
  id: string;
  name: string;
  short_name?: string;
  slug: string;
  official_website: string;
  institution_type: string;
  ownership_type: string;
  country: string;
  state?: string;
  city?: string;
  address?: string;
  accreditation?: string;
  recognition?: string;
  description?: string;
  established_year?: number;
  logo_url?: string;
  data_completeness_score: number;
  last_scanned_at?: string;
  admission_status?: string;
  has_scholarships?: boolean;
  programs_count?: number;
  faculty_count?: number;
  created_at: string;
}

export interface TraceableFact {
  category: string;
  field_name: string;
  value: string;
  source_url: string;
  source_page_title?: string;
  confidence_score: number;
  verification_status: string;
  academic_year?: string;
  last_verified_at?: string;
}

export interface UniversityProfile extends UniversitySummary {
  admissions: any[];
  programs: any[];
  scholarships: any[];
  faculty: any[];
  placements: any[];
  facilities: any[];
  research_projects: any[];
  notifications: any[];
  contacts: any[];
  traceable_facts: TraceableFact[];
}

export interface ExtractedFactPreview {
  category: string;
  field_name: string;
  extracted_value: string;
  source_url: string;
  confidence_score: number;
  verification_status: string;
}

export interface ExtractedSummary {
  university_id: string;
  university_name: string;
  city?: string;
  state?: string;
  official_website?: string;
  data_completeness_score: number;
  admissions_count: number;
  programs_count: number;
  scholarships_count: number;
  faculty_count: number;
  placements_count: number;
  recent_records: ExtractedFactPreview[];
}

export interface CrawlJobStatus {
  job_id: string;
  seed_url: string;
  status: string;
  pages_discovered: number;
  pages_crawled: number;
  records_extracted: number;
  needs_review_count: number;
  errors_count: number;
  max_depth: number;
  max_pages: number;
  start_time?: string;
  end_time?: string;
  duration_seconds?: number;
  university_id?: string;
  university_name?: string;
  university_slug?: string;
  extracted_summary?: ExtractedSummary;
  error_details?: string;
  logs: { level: string; message: string; timestamp: string }[];
}

export interface QualityMetrics {
  total_institutions: number;
  total_crawled_pages: number;
  total_extracted_records: number;
  verified_records: number;
  needs_review_records: number;
  outdated_records: number;
  conflicting_records: number;
  duplicate_records_detected: number;
  average_completeness_score: number;
  category_breakdown: Record<string, number>;
  recent_conflicts: any[];
}

export async function fetchUniversities(params: {
  query?: string;
  country?: string;
  state?: string;
  city?: string;
  institution_type?: string;
  admission_status?: string;
  degree_type?: string;
  page?: number;
  page_size?: number;
} = {}) {
  try {
    const queryParams = new URLSearchParams();
    if (params.query) queryParams.set("query", params.query);
    if (params.country) queryParams.set("country", params.country);
    if (params.state) queryParams.set("state", params.state);
    if (params.city) queryParams.set("city", params.city);
    if (params.institution_type) queryParams.set("institution_type", params.institution_type);
    if (params.admission_status) queryParams.set("admission_status", params.admission_status);
    if (params.degree_type) queryParams.set("degree_type", params.degree_type);
    if (params.page) queryParams.set("page", params.page.toString());
    if (params.page_size) queryParams.set("page_size", params.page_size.toString());

    const res = await fetch(`${API_BASE}/universities?${queryParams.toString()}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch universities");
    return await res.json();
  } catch (err) {
    console.warn("Backend API offline or unreachable, returning empty results:", err);
    return { total: 0, page: 1, page_size: 12, total_pages: 1, results: [] };
  }
}

export async function fetchUniversityProfile(id: string): Promise<UniversityProfile | null> {
  try {
    const res = await fetch(`${API_BASE}/universities/${id}`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error("Error fetching university profile:", err);
    return null;
  }
}

export async function startCrawlJob(url: string, maxDepth: number = 2, maxPages: number = 25, universityName?: string) {
  // Use longer timeout for Render cold-start (free tier can take ~30s to wake)
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 45000);

  try {
    const res = await fetch(`${API_BASE}/crawl/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, max_depth: maxDepth, max_pages: maxPages, university_name: universityName }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Crawl request failed" }));
      throw new Error(err.detail || "Failed to start crawler");
    }
    return await res.json();
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err.name === "AbortError") {
      throw new Error("Backend server is waking up (Render free tier cold-start). Please wait 30 seconds and try again.");
    }
    throw err;
  }
}

export async function fetchCrawlStatus(jobId: string): Promise<CrawlJobStatus | null> {
  try {
    const res = await fetch(`${API_BASE}/crawl/status/${jobId}`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function fetchDataQuality(): Promise<QualityMetrics | null> {
  try {
    const res = await fetch(`${API_BASE}/data-quality`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function compareColleges(universityIds: string[]) {
  const res = await fetch(`${API_BASE}/universities/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ university_ids: universityIds })
  });
  if (!res.ok) throw new Error("Failed to compare institutions");
  return await res.json();
}

export async function fetchMonitoringChanges() {
  try {
    const res = await fetch(`${API_BASE}/monitoring/changes`, { cache: "no-store" });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function fetchAdminStats() {
  try {
    const res = await fetch(`${API_BASE}/admin/stats`, { cache: "no-store" });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function rescanUniversity(id: string) {
  const res = await fetch(`${API_BASE}/universities/${id}/rescan`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to initiate rescan");
  return await res.json();
}

export interface CollegeSuggestion {
  id?: string;
  name: string;
  short_name?: string;
  city?: string;
  state?: string;
  official_website?: string;
  slug?: string;
  institution_type?: string;
  data_completeness_score?: number;
  is_in_database: boolean;
}

export interface URLResolveResponse {
  name: string;
  official_website: string;
  domain: string;
  confidence: number;
  source: string;
  is_accessible: boolean;
  note?: string;
}

export interface RecommendedInstitution {
  name: string;
  location?: string;
  official_website?: string;
  key_highlights?: string;
  why_recommended?: string;
  matched_id?: string;
}

export interface AISearchResponse {
  query: string;
  ai_answer: string;
  recommended_institutions: RecommendedInstitution[];
  matched_colleges: UniversitySummary[];
  confidence: number;
  source: string;
}

export async function fetchSuggestions(query: string, limit = 8): Promise<CollegeSuggestion[]> {
  if (!query || query.trim().length === 0) return [];
  try {
    const res = await fetch(`${API_BASE}/universities/suggest?query=${encodeURIComponent(query.trim())}&limit=${limit}`);
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function resolveCollegeUrl(name: string, apiKey?: string): Promise<URLResolveResponse> {
  const params = new URLSearchParams({ name: name.trim() });
  if (apiKey) params.append("api_key", apiKey.trim());
  const res = await fetch(`${API_BASE}/universities/resolve-url?${params.toString()}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Could not automatically resolve official website.");
  }
  return await res.json();
}

export async function performAISearch(query: string, apiKey?: string): Promise<AISearchResponse> {
  const res = await fetch(`${API_BASE}/universities/ai-search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: query.trim(),
      api_key: apiKey ? apiKey.trim() : undefined
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "AI search failed to process inquiry.");
  }
  return await res.json();
}
