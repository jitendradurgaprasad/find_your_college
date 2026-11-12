"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Scale, 
  Plus, 
  Trash2, 
  Building2, 
  MapPin, 
  ExternalLink, 
  Award, 
  CheckCircle2, 
  Clock, 
  BookOpen, 
  Briefcase, 
  Home, 
  Sparkles,
  ArrowRight
} from "lucide-react";
import { fetchUniversities, compareColleges, UniversitySummary } from "@/lib/api";

export default function ComparePage() {
  const [allColleges, setAllColleges] = useState<UniversitySummary[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [comparisonData, setComparisonData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);

  useEffect(() => {
    async function init() {
      try {
        const data = await fetchUniversities({ page_size: 20 });
        if (data && data.results) {
          setAllColleges(data.results);
          // Pre-select first 2 colleges for instant demo comparison
          if (data.results.length >= 2) {
            const initialIds = [data.results[0].id, data.results[1].id];
            setSelectedIds(initialIds);
            const res = await compareColleges(initialIds);
            setComparisonData(res.colleges || []);
          }
        }
      } catch (err) {
        console.error("Failed to load colleges for comparison:", err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  const handleToggleSelect = async (id: string) => {
    let newSelected: string[];
    if (selectedIds.includes(id)) {
      newSelected = selectedIds.filter((item) => item !== id);
    } else {
      if (selectedIds.length >= 4) {
        alert("You can compare up to 4 institutions simultaneously.");
        return;
      }
      newSelected = [...selectedIds, id];
    }
    setSelectedIds(newSelected);

    if (newSelected.length > 0) {
      setComparing(true);
      try {
        const res = await compareColleges(newSelected);
        setComparisonData(res.colleges || []);
      } catch (err) {
        console.error("Comparison request failed:", err);
      } finally {
        setComparing(false);
      }
    } else {
      setComparisonData([]);
    }
  };

  const removeCollege = async (id: string) => {
    handleToggleSelect(id);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Page Header */}
      <div className="space-y-1.5">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
          <Scale className="h-3.5 w-3.5" />
          <span>Multi-Institution Side-by-Side Analysis</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          College Comparison Engine
        </h1>
        <p className="text-sm text-slate-500 leading-relaxed max-w-2xl">
          Evaluate colleges side-by-side on verified parameters: tuition fees, admission status, placement rates, and scholarship availability. Missing data is clearly marked without assumptions.
        </p>
      </div>

      {/* College Selector Bar */}
      <div className="p-5 bg-white rounded-3xl border border-slate-200 shadow-sm space-y-3">
        <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
          Select Institutions to Compare (Max 4):
        </span>
        <div className="flex flex-wrap gap-2 pt-1">
          {allColleges.map((c) => {
            const isSelected = selectedIds.includes(c.id);
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => handleToggleSelect(c.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition border ${
                  isSelected
                    ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                    : "bg-slate-50 text-slate-700 border-slate-200 hover:border-blue-400"
                }`}
              >
                <span>{c.short_name || c.name}</span>
                {isSelected ? <Trash2 className="h-3 w-3" /> : <Plus className="h-3 w-3" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* COMPARISON MATRIX TABLE */}
      {comparisonData.length > 0 ? (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              {/* Institution Headers */}
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/50">
                  <th className="p-4 w-52 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                    Dimension
                  </th>
                  {comparisonData.map((col) => (
                    <th key={col.id} className="p-4 min-w-[240px] align-top">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                            {col.institution_type}
                          </span>
                          <button
                            type="button"
                            onClick={() => removeCollege(col.id)}
                            className="text-slate-400 hover:text-rose-600 transition"
                            title="Remove from comparison"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                        <h3 className="text-sm font-bold text-slate-900 leading-snug">{col.name}</h3>
                        <div className="flex items-center gap-1 text-[11px] text-slate-500">
                          <MapPin className="h-3 w-3" />
                          <span>{col.location}</span>
                        </div>
                        <Link
                          href={`/colleges/${col.id}`}
                          className="inline-flex items-center gap-1 text-[11px] font-semibold text-blue-600 hover:underline pt-1"
                        >
                          <span>Full Profile</span>
                          <ArrowRight className="h-3 w-3" />
                        </Link>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100">
                {/* 1. Admission Status */}
                <tr>
                  <td className="p-4 font-bold text-slate-800 bg-slate-50/30">Admissions Status</td>
                  {comparisonData.map((col) => (
                    <td key={col.id} className="p-4 font-bold uppercase text-blue-600">
                      {col.admission_status} ({col.academic_year})
                    </td>
                  ))}
                </tr>

                {/* 2. Accreditation */}
                <tr>
                  <td className="p-4 font-bold text-slate-800 bg-slate-50/30">Accreditation</td>
                  {comparisonData.map((col) => (
                    <td key={col.id} className="p-4 text-slate-700">
                      {col.accreditation}
                    </td>
                  ))}
                </tr>

                {/* 3. Tuition Fee Range */}
                <tr>
                  <td className="p-4 font-bold text-slate-800 bg-slate-50/30">Tuition Fees</td>
                  {comparisonData.map((col) => (
                    <td key={col.id} className="p-4 font-medium text-slate-800">
                      {col.tuition_fee_range}
                    </td>
                  ))}
                </tr>

                {/* 4. Placement Rate */}
                <tr>
                  <td className="p-4 font-bold text-slate-800 bg-slate-50/30">Placement Rate</td>
                  {comparisonData.map((col) => (
                    <td key={col.id} className="p-4 font-bold text-emerald-600">
                      {col.placement_rate}
                    </td>
                  ))}
                </tr>

                {/* 5. Highest Package */}
                <tr>
                  <td className="p-4 font-bold text-slate-800 bg-slate-50/30">Highest Package</td>
                  {comparisonData.map((col) => (
                    <td key={col.id} className="p-4 font-bold text-slate-900">
                      {col.highest_package}
                    </td>
                  ))}
                </tr>

                {/* 6. Average Package */}
                <tr>
                  <td className="p-4 font-bold text-slate-800 bg-slate-50/30">Average Package</td>
                  {comparisonData.map((col) => (
                    <td key={col.id} className="p-4 font-semibold text-slate-800">
                      {col.average_package}
                    </td>
                  ))}
                </tr>

                {/* 7. Scholarships Available */}
                <tr>
                  <td className="p-4 font-bold text-slate-800 bg-slate-50/30">Scholarships Schemes</td>
                  {comparisonData.map((col) => (
                    <td key={col.id} className="p-4 text-slate-700">
                      {col.scholarships_count} Schemes Indexed
                    </td>
                  ))}
                </tr>

                {/* 8. Programs Offered */}
                <tr>
                  <td className="p-4 font-bold text-slate-800 bg-slate-50/30">Sample Programs</td>
                  {comparisonData.map((col) => (
                    <td key={col.id} className="p-4 text-slate-600 space-y-1">
                      {col.sample_programs.length > 0 ? (
                        col.sample_programs.map((prog: string, pIdx: number) => (
                          <div key={pIdx} className="truncate">• {prog}</div>
                        ))
                      ) : (
                        <div>Information unavailable</div>
                      )}
                    </td>
                  ))}
                </tr>

                {/* 9. Facilities */}
                <tr>
                  <td className="p-4 font-bold text-slate-800 bg-slate-50/30">Campus Facilities</td>
                  {comparisonData.map((col) => (
                    <td key={col.id} className="p-4 text-slate-600">
                      {col.facilities.length > 0 ? col.facilities.join(", ") : "Information unavailable"}
                    </td>
                  ))}
                </tr>

                {/* 10. Completeness Score */}
                <tr>
                  <td className="p-4 font-bold text-slate-800 bg-slate-50/30">Data Completeness</td>
                  {comparisonData.map((col) => (
                    <td key={col.id} className="p-4 font-bold text-emerald-600">
                      {Math.round(col.data_completeness_score)}% Complete
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="p-16 text-center bg-white rounded-3xl border border-slate-200 space-y-3">
          <Scale className="h-12 w-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">No institutions selected for comparison</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Choose at least two colleges from the selector above to perform a side-by-side analysis.
          </p>
        </div>
      )}
    </div>
  );
}
