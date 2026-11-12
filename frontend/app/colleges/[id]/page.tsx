"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  Building2, 
  MapPin, 
  ExternalLink, 
  Calendar, 
  Clock, 
  BookOpen, 
  Award, 
  Users, 
  Briefcase, 
  Home, 
  FileText, 
  Phone, 
  Mail, 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  RotateCw, 
  Bookmark, 
  GraduationCap, 
  Layers,
  Sparkles,
  Info
} from "lucide-react";
import VerificationBadge from "@/components/VerificationBadge";
import { fetchUniversityProfile, rescanUniversity, UniversityProfile } from "@/lib/api";

export default function CollegeProfilePage() {
  const params = useParams();
  const router = useRouter();
  const collegeId = params.id as string;

  const [profile, setProfile] = useState<UniversityProfile | null>(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [rescanStatus, setRescanStatus] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function loadProfile() {
      setLoading(true);
      try {
        const data = await fetchUniversityProfile(collegeId);
        setProfile(data);
      } catch (err) {
        console.error("Failed to load profile:", err);
      } finally {
        setLoading(false);
      }
    }
    if (collegeId) loadProfile();
  }, [collegeId]);

  const handleRescan = async () => {
    if (!profile) return;
    try {
      setRescanStatus("Initiating rescan job...");
      const res = await rescanUniversity(profile.id);
      setRescanStatus(`Rescan queued! Job ID: ${res.job_id.substring(0, 8)}...`);
      setTimeout(() => setRescanStatus(null), 5000);
    } catch (err: any) {
      setRescanStatus(err.message || "Failed to start rescan");
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 space-y-8 animate-pulse">
        <div className="h-40 rounded-3xl bg-slate-200" />
        <div className="h-12 w-96 rounded-xl bg-slate-200" />
        <div className="h-96 rounded-3xl bg-slate-200" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center space-y-4">
        <Building2 className="h-14 w-14 text-slate-300 mx-auto" />
        <h2 className="text-xl font-bold text-slate-900">Institution Not Found</h2>
        <p className="text-xs text-slate-500">
          The requested college profile could not be retrieved from the indexed database.
        </p>
        <Link href="/search" className="inline-block px-4 py-2 text-xs font-semibold bg-blue-600 text-white rounded-xl">
          Back to College Search
        </Link>
      </div>
    );
  }

  const tabs = [
    { id: "overview", label: "Overview", icon: Building2 },
    { id: "admissions", label: "Admissions", icon: Clock },
    { id: "courses", label: "Courses & Degrees", icon: BookOpen },
    { id: "scholarships", label: "Scholarships", icon: Award },
    { id: "faculty", label: "Faculty Directory", icon: Users },
    { id: "departments", label: "Departments", icon: Layers },
    { id: "research", label: "Research & Labs", icon: Sparkles },
    { id: "placements", label: "Placements", icon: Briefcase },
    { id: "facilities", label: "Campus & Facilities", icon: Home },
    { id: "notifications", label: "Notifications", icon: FileText },
    { id: "contact", label: "Contacts & Office", icon: Phone },
  ];

  const completeness = Math.round(profile.data_completeness_score || 0);

  const renderEmptyState = (category: string) => (
    <div className="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200 space-y-2">
      <Info className="h-6 w-6 text-slate-400 mx-auto" />
      <p className="text-xs font-medium text-slate-600">
        Information is currently unavailable from the indexed sources.
      </p>
      <p className="text-[11px] text-slate-400">
        No verified {category.toLowerCase()} facts were identified on publicly reachable official pages during the last crawl.
      </p>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* INSTITUTION HEADER BANNER */}
      <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start gap-5">
            <div className="h-20 w-20 rounded-2xl bg-slate-50 border border-slate-200 flex-shrink-0 flex items-center justify-center p-2 overflow-hidden shadow-inner">
              {profile.logo_url ? (
                <img src={profile.logo_url} alt={profile.name} className="h-16 w-16 object-contain" />
              ) : (
                <GraduationCap className="h-10 w-10 text-slate-400" />
              )}
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
                  {profile.institution_type || "University"}
                </span>
                {profile.ownership_type && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                    {profile.ownership_type}
                  </span>
                )}
                {profile.accreditation && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {profile.accreditation}
                  </span>
                )}
              </div>

              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                {profile.name}
              </h1>

              {(profile.city || profile.state) && (
                <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
                  <MapPin className="h-3.5 w-3.5 text-slate-400" />
                  <span>{profile.city ? `${profile.city}, ` : ""}{profile.state || profile.country}</span>
                  {profile.established_year && (
                    <>
                      <span>•</span>
                      <span>Est. {profile.established_year}</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Action CTAs & Completeness Bar */}
          <div className="flex flex-col sm:flex-row md:flex-col items-start md:items-end gap-3 flex-shrink-0">
            <div className="flex items-center gap-2">
              <a
                href={profile.official_website}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold transition"
              >
                <span>Official Website</span>
                <ExternalLink className="h-3.5 w-3.5" />
              </a>

              <button
                type="button"
                onClick={handleRescan}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition active:scale-95"
              >
                <RotateCw className="h-3.5 w-3.5" />
                <span>Rescan</span>
              </button>
            </div>

            {rescanStatus && (
              <div className="text-[11px] font-medium text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-200">
                {rescanStatus}
              </div>
            )}

            {/* Completeness Score */}
            <div className="flex items-center gap-2 text-xs font-medium text-slate-600 mt-1">
              <Sparkles className="h-3.5 w-3.5 text-emerald-600" />
              <span>Data Completeness: <strong className="text-slate-900 font-bold">{completeness}%</strong></span>
              <div className="w-16 h-2 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${completeness}%` }} />
              </div>
            </div>
          </div>
        </div>

        {/* Audit Meta Bar */}
        <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-600" />
            <span>Extracted facts verified against published institutional sources.</span>
          </div>
          <div>
            Last Scanned: <strong className="text-slate-700">{profile.last_scanned_at ? new Date(profile.last_scanned_at).toLocaleDateString() : "Recently Verified"}</strong>
          </div>
        </div>
      </div>

      {/* 11 PROFILE TABS NAVIGATION */}
      <div className="border-b border-slate-200 overflow-x-auto scrollbar-none">
        <nav className="flex space-x-2 min-w-max pb-1">
          {tabs.map((t) => {
            const Icon = t.icon;
            const isActive = activeTab === t.id;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setActiveTab(t.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition ${
                  isActive
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? "text-white" : "text-slate-400"}`} />
                {t.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* TAB CONTENT PANELS */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-6 min-h-[400px]">
        {/* 1. OVERVIEW TAB */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">About the Institution</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                {profile.description || "Official institution profile discovered and indexed by Find Your Collage crawler."}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-100">
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-xs text-slate-500 font-medium">Accreditation</span>
                <p className="text-sm font-bold text-slate-900">{profile.accreditation || "Information unavailable"}</p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-xs text-slate-500 font-medium">Recognition</span>
                <p className="text-sm font-bold text-slate-900">{profile.recognition || "UGC / Ministry of Education"}</p>
              </div>
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-xs text-slate-500 font-medium">Campus Location</span>
                <p className="text-sm font-bold text-slate-900">{profile.address || `${profile.city}, ${profile.state}`}</p>
              </div>
            </div>

            {/* Traceable Fact Highlights */}
            {profile.traceable_facts && profile.traceable_facts.length > 0 && (
              <div className="pt-4 border-t border-slate-100 space-y-3">
                <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-600" />
                  <span>Audited Fact Traceability</span>
                </h4>
                <div className="divide-y divide-slate-100 rounded-2xl border border-slate-200 overflow-hidden">
                  {profile.traceable_facts.slice(0, 5).map((f, i) => (
                    <div key={i} className="p-3 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-white">
                      <div>
                        <span className="font-semibold text-slate-800">{f.category} / {f.field_name}: </span>
                        <span className="text-slate-600">{f.value}</span>
                      </div>
                      <VerificationBadge
                        status={f.verification_status}
                        sourceUrl={f.source_url}
                        academicYear={f.academic_year}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 2. ADMISSIONS TAB */}
        {activeTab === "admissions" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-900">Admission Announcements & Criteria</h3>
            </div>

            {profile.admissions && profile.admissions.length > 0 ? (
              <div className="space-y-4">
                {profile.admissions.map((adm, idx) => (
                  <div key={idx} className="p-5 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div>
                        <span className="text-xs font-bold uppercase tracking-wider text-blue-600">
                          Academic Year {adm.academic_year}
                        </span>
                        <h4 className="text-base font-bold text-slate-900 mt-0.5">{adm.title}</h4>
                      </div>
                      <VerificationBadge status={adm.verification_status} sourceUrl={adm.source_url} />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
                      <div className="p-3 rounded-xl bg-white border border-slate-200">
                        <span className="text-slate-500 font-medium">Status</span>
                        <p className="text-sm font-extrabold text-slate-900 uppercase mt-0.5">{adm.admission_status}</p>
                      </div>
                      <div className="p-3 rounded-xl bg-white border border-slate-200">
                        <span className="text-slate-500 font-medium">Entrance Exams</span>
                        <p className="text-sm font-semibold text-slate-900 mt-0.5">{adm.entrance_exams || "Information unavailable"}</p>
                      </div>
                      <div className="p-3 rounded-xl bg-white border border-slate-200">
                        <span className="text-slate-500 font-medium">Application Fee</span>
                        <p className="text-sm font-semibold text-slate-900 mt-0.5">{adm.application_fee || "Information unavailable"}</p>
                      </div>
                    </div>

                    {adm.source_evidence && (
                      <div className="p-3 rounded-xl bg-blue-50/60 border border-blue-200 text-xs text-blue-900">
                        <strong>Source Evidence:</strong> <em>&quot;{adm.source_evidence}&quot;</em>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : renderEmptyState("Admissions")}
          </div>
        )}

        {/* 3. COURSES TAB */}
        {activeTab === "courses" && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-900">Offered Programs & Degrees</h3>
            {profile.programs && profile.programs.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {profile.programs.map((p, idx) => (
                  <div key={idx} className="p-5 rounded-2xl border border-slate-200 bg-white space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                        {p.degree_type}
                      </span>
                      {p.duration_years && (
                        <span className="text-xs text-slate-500">{p.duration_years} Years Duration</span>
                      )}
                    </div>
                    <h4 className="text-base font-bold text-slate-900">{p.name}</h4>
                    {p.specialization && (
                      <p className="text-xs text-slate-600">Specialization: <strong>{p.specialization}</strong></p>
                    )}
                    <div className="text-xs text-slate-500 pt-2 border-t border-slate-100 flex items-center justify-between">
                      <span>Tuition Fee: <strong>{p.tuition_fees_annual || "Published officially"}</strong></span>
                      {p.source_url && (
                        <a href={p.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-0.5">
                          <span>Syllabus</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : renderEmptyState("Course & Program")}
          </div>
        )}

        {/* 4. SCHOLARSHIPS TAB */}
        {activeTab === "scholarships" && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-900">Scholarships & Financial Aid</h3>
            {profile.scholarships && profile.scholarships.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {profile.scholarships.map((s, idx) => (
                  <div key={idx} className="p-5 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                        {s.provider_type} Scholarship
                      </span>
                      <VerificationBadge status={s.verification_status} sourceUrl={s.source_url} />
                    </div>
                    <h4 className="text-base font-bold text-slate-900">{s.name}</h4>
                    <p className="text-xs text-slate-600 leading-relaxed">{s.description}</p>
                    <div className="p-3 rounded-xl bg-white border border-slate-200 text-xs text-slate-800 font-semibold">
                      Amount: {s.scholarship_amount || "Fee waiver as per norms"}
                    </div>
                  </div>
                ))}
              </div>
            ) : renderEmptyState("Scholarship")}
          </div>
        )}

        {/* 5. FACULTY TAB */}
        {activeTab === "faculty" && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-900">Faculty Members & Researchers</h3>
            {profile.faculty && profile.faculty.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {profile.faculty.map((f, idx) => (
                  <div key={idx} className="p-4 rounded-2xl border border-slate-200 bg-white space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-blue-600">{f.designation || "Faculty"}</span>
                      {f.source_url && (
                        <a href={f.source_url} target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-blue-600">
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </div>
                    <h4 className="text-sm font-bold text-slate-900">{f.name}</h4>
                    {f.qualifications && <p className="text-xs text-slate-500">{f.qualifications}</p>}
                    {f.specialization && <p className="text-xs text-slate-600 font-medium">{f.specialization}</p>}
                    {f.official_email && (
                      <p className="text-[11px] text-blue-600 truncate pt-2 border-t border-slate-100">{f.official_email}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : renderEmptyState("Faculty")}
          </div>
        )}

        {/* 6. DEPARTMENTS TAB */}
        {activeTab === "departments" && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-900">Academic Departments & Schools</h3>
            {renderEmptyState("Department")}
          </div>
        )}

        {/* 7. RESEARCH TAB */}
        {activeTab === "research" && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-900">Research Projects & Innovation</h3>
            {profile.research_projects && profile.research_projects.length > 0 ? (
              <div className="space-y-4">
                {profile.research_projects.map((rp, idx) => (
                  <div key={idx} className="p-4 rounded-2xl border border-slate-200 space-y-2">
                    <h4 className="text-sm font-bold text-slate-900">{rp.title}</h4>
                    <p className="text-xs text-slate-600">{rp.description}</p>
                  </div>
                ))}
              </div>
            ) : renderEmptyState("Research Project")}
          </div>
        )}

        {/* 8. PLACEMENTS TAB */}
        {activeTab === "placements" && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-900">Placement Statistics & Recruiters</h3>
            {profile.placements && profile.placements.length > 0 ? (
              <div className="space-y-6">
                {profile.placements.map((plc, idx) => (
                  <div key={idx} className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                        Reporting Period: Academic Year {plc.academic_year}
                      </span>
                      <VerificationBadge status={plc.verification_status} sourceUrl={plc.source_url} />
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="p-4 rounded-2xl bg-blue-50/60 border border-blue-200">
                        <span className="text-xs text-blue-700 font-semibold">Placement Rate</span>
                        <p className="text-2xl font-extrabold text-blue-900 mt-1">
                          {plc.placement_percentage ? `${plc.placement_percentage}%` : "Information unavailable"}
                        </p>
                      </div>
                      <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200">
                        <span className="text-xs text-emerald-700 font-semibold">Highest Package</span>
                        <p className="text-lg font-extrabold text-emerald-900 mt-1">
                          {plc.highest_package || "Information unavailable"}
                        </p>
                      </div>
                      <div className="p-4 rounded-2xl bg-indigo-50/60 border border-indigo-200">
                        <span className="text-xs text-indigo-700 font-semibold">Average Package</span>
                        <p className="text-lg font-extrabold text-indigo-900 mt-1">
                          {plc.average_package || "Information unavailable"}
                        </p>
                      </div>
                      <div className="p-4 rounded-2xl bg-amber-50/60 border border-amber-200">
                        <span className="text-xs text-amber-700 font-semibold">Median Package</span>
                        <p className="text-lg font-extrabold text-amber-900 mt-1">
                          {plc.median_package || "Information unavailable"}
                        </p>
                      </div>
                    </div>

                    {plc.recruiting_companies && plc.recruiting_companies.length > 0 && (
                      <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                        <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                          Key Recruiting Companies
                        </span>
                        <div className="flex flex-wrap gap-2 pt-1">
                          {plc.recruiting_companies.map((comp: string, cIdx: number) => (
                            <span key={cIdx} className="px-3 py-1 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-800 shadow-2xs">
                              {comp}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : renderEmptyState("Placement Statistics")}
          </div>
        )}

        {/* 9. FACILITIES TAB */}
        {activeTab === "facilities" && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-900">Campus Facilities & Infrastructure</h3>
            {profile.facilities && profile.facilities.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {profile.facilities.map((fac, idx) => (
                  <div key={idx} className="p-5 rounded-2xl border border-slate-200 bg-white space-y-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                      {fac.facility_type}
                    </span>
                    <h4 className="text-base font-bold text-slate-900 mt-1">{fac.name}</h4>
                    <p className="text-xs text-slate-600 leading-relaxed">{fac.description}</p>
                    {fac.features && (
                      <ul className="text-xs text-slate-500 list-disc list-inside space-y-0.5 pt-1">
                        {fac.features.map((ft: string, fIdx: number) => (
                          <li key={fIdx}>{ft}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            ) : renderEmptyState("Facility")}
          </div>
        )}

        {/* 10. NOTIFICATIONS TAB */}
        {activeTab === "notifications" && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-900">Important Notices & Circulars</h3>
            {profile.notifications && profile.notifications.length > 0 ? (
              <div className="space-y-3">
                {profile.notifications.map((notif, idx) => (
                  <div key={idx} className="p-4 rounded-2xl border border-slate-200 bg-white flex items-center justify-between">
                    <div>
                      <span className="text-[11px] font-bold text-blue-600 uppercase">{notif.category}</span>
                      <h4 className="text-sm font-bold text-slate-900">{notif.title}</h4>
                    </div>
                    {notif.source_url && (
                      <a href={notif.source_url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline flex items-center gap-1 font-semibold">
                        <span>Notice</span>
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            ) : renderEmptyState("Notification")}
          </div>
        )}

        {/* 11. CONTACT TAB */}
        {activeTab === "contact" && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-900">Institutional Contacts & Offices</h3>
            {profile.contacts && profile.contacts.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {profile.contacts.map((c, idx) => (
                  <div key={idx} className="p-5 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-2 text-xs">
                    <h4 className="text-sm font-bold text-slate-900">{c.office_name}</h4>
                    {c.email && (
                      <p className="flex items-center gap-2 text-slate-700">
                        <Mail className="h-3.5 w-3.5 text-slate-400" />
                        <span>{c.email}</span>
                      </p>
                    )}
                    {c.phone && (
                      <p className="flex items-center gap-2 text-slate-700">
                        <Phone className="h-3.5 w-3.5 text-slate-400" />
                        <span>{c.phone}</span>
                      </p>
                    )}
                    {c.address && (
                      <p className="flex items-center gap-2 text-slate-500">
                        <MapPin className="h-3.5 w-3.5 text-slate-400" />
                        <span>{c.address}</span>
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : renderEmptyState("Contact")}
          </div>
        )}
      </div>
    </div>
  );
}
