import Link from "next/link";
import { 
  MapPin, 
  ExternalLink, 
  GraduationCap, 
  Award, 
  Calendar, 
  BookOpen, 
  CheckCircle2, 
  Clock, 
  Sparkles,
  ArrowRight
} from "lucide-react";
import { UniversitySummary } from "@/lib/api";

interface CardProps {
  college: UniversitySummary;
}

export default function CollegeCard({ college }: CardProps) {
  const getStatusColor = (status?: string) => {
    switch (status?.toUpperCase()) {
      case "OPEN":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "ONGOING":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "UPCOMING":
        return "bg-indigo-50 text-indigo-700 border-indigo-200";
      case "CLOSED":
        return "bg-rose-50 text-rose-700 border-rose-200";
      default:
        return "bg-slate-50 text-slate-600 border-slate-200";
    }
  };

  const completeness = Math.round(college.data_completeness_score || 0);

  return (
    <div className="group bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-blue-300 transition-all duration-200 flex flex-col justify-between overflow-hidden">
      <div className="p-5">
        {/* Header: Logo, Name & Type */}
        <div className="flex items-start gap-3.5 mb-3">
          <div className="h-12 w-12 rounded-xl bg-slate-100 border border-slate-200 flex-shrink-0 flex items-center justify-center overflow-hidden">
            {college.logo_url ? (
              <img src={college.logo_url} alt={college.name} className="h-10 w-10 object-contain" />
            ) : (
              <GraduationCap className="h-6 w-6 text-slate-400 group-hover:text-blue-600 transition" />
            )}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[11px] font-semibold tracking-wide uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                {college.institution_type || "University"}
              </span>
              {college.ownership_type && (
                <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-50 text-slate-600 border border-slate-200">
                  {college.ownership_type}
                </span>
              )}
            </div>

            <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition truncate mt-1">
              {college.name}
            </h3>

            {(college.city || college.state) && (
              <div className="flex items-center gap-1 text-xs text-slate-500 mt-0.5">
                <MapPin className="h-3.5 w-3.5 text-slate-400 flex-shrink-0" />
                <span className="truncate">{college.city ? `${college.city}, ` : ""}{college.state || college.country}</span>
              </div>
            )}
          </div>
        </div>

        {/* Description Snippet */}
        <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed mb-4">
          {college.description || "Official institution profile discovered and indexed by Find Your Collage crawler."}
        </p>

        {/* Badges / Highlights Grid */}
        <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
          {/* Admission Status */}
          <div className={`p-2 rounded-xl border flex items-center justify-between ${getStatusColor(college.admission_status)}`}>
            <div className="flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5" />
              <span className="text-[11px] font-medium">Admissions</span>
            </div>
            <span className="text-[11px] font-bold uppercase">{college.admission_status || "UNKNOWN"}</span>
          </div>

          {/* Scholarship Status */}
          <div className="p-2 rounded-xl border border-slate-200 bg-slate-50 text-slate-700 flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Award className="h-3.5 w-3.5 text-amber-500" />
              <span className="text-[11px] font-medium">Scholarships</span>
            </div>
            <span className="text-[11px] font-semibold text-slate-900">
              {college.has_scholarships ? "Available" : "Check Profile"}
            </span>
          </div>
        </div>

        {/* Accreditation & Stats Bar */}
        <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-100">
          <div className="flex items-center gap-1.5 truncate">
            <BookOpen className="h-3.5 w-3.5 text-slate-400" />
            <span>{college.programs_count ? `${college.programs_count} Programs` : "Programs Indexed"}</span>
          </div>
          <div className="flex items-center gap-1.5 text-emerald-600 font-medium">
            <Sparkles className="h-3.5 w-3.5" />
            <span>{completeness}% Complete</span>
          </div>
        </div>
      </div>

      {/* Card Footer Actions */}
      <div className="bg-slate-50/80 px-5 py-3 border-t border-slate-100 flex items-center justify-between">
        <a
          href={college.official_website}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-slate-500 hover:text-blue-600 flex items-center gap-1 font-medium transition"
        >
          <span>Official Web</span>
          <ExternalLink className="h-3 w-3" />
        </a>

        <Link
          href={`/colleges/${college.slug || college.id}`}
          className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition group-hover:translate-x-0.5"
        >
          <span>Explore Profile</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </div>
  );
}
