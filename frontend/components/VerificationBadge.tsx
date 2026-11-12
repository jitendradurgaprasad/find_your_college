import { CheckCircle2, AlertCircle, Clock, AlertTriangle, ExternalLink } from "lucide-react";

interface BadgeProps {
  status: string;
  sourceUrl?: string;
  confidenceScore?: number;
  academicYear?: string;
}

export default function VerificationBadge({ status, sourceUrl, confidenceScore, academicYear }: BadgeProps) {
  const normStatus = (status || "UNVERIFIED").toUpperCase();

  const getStatusConfig = () => {
    switch (normStatus) {
      case "VERIFIED":
        return {
          bg: "bg-emerald-50 text-emerald-700 border-emerald-200",
          icon: CheckCircle2,
          label: "VERIFIED"
        };
      case "NEEDS_REVIEW":
        return {
          bg: "bg-amber-50 text-amber-700 border-amber-200",
          icon: AlertCircle,
          label: "NEEDS REVIEW"
        };
      case "OUTDATED":
        return {
          bg: "bg-slate-100 text-slate-600 border-slate-200",
          icon: Clock,
          label: "OUTDATED"
        };
      case "CONFLICTING":
        return {
          bg: "bg-rose-50 text-rose-700 border-rose-200",
          icon: AlertTriangle,
          label: "CONFLICTING"
        };
      default:
        return {
          bg: "bg-gray-50 text-gray-600 border-gray-200",
          icon: AlertCircle,
          label: "UNVERIFIED"
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div className="inline-flex items-center gap-1.5 flex-wrap">
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${config.bg}`}>
        <Icon className="h-3 w-3" />
        {config.label}
      </span>

      {academicYear && (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
          AY {academicYear}
        </span>
      )}

      {sourceUrl && (
        <a
          href={sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          title={`Extracted from: ${sourceUrl}`}
          className="inline-flex items-center gap-0.5 text-[11px] text-blue-600 hover:text-blue-800 hover:underline font-medium"
        >
          <span>Source</span>
          <ExternalLink className="h-2.5 w-2.5" />
        </a>
      )}
    </div>
  );
}
