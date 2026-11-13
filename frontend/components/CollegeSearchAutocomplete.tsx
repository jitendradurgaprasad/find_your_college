"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search, Building2, MapPin, CheckCircle2, Globe, Sparkles, Loader2, X } from "lucide-react";
import { fetchSuggestions, CollegeSuggestion } from "@/lib/api";

interface CollegeSearchAutocompleteProps {
  value: string;
  onChange: (val: string) => void;
  onSelect?: (college: CollegeSuggestion) => void;
  placeholder?: string;
  autoNavigate?: boolean;
  className?: string;
  inputClassName?: string;
  showIcon?: boolean;
}

export default function CollegeSearchAutocomplete({
  value,
  onChange,
  onSelect,
  placeholder = "Search colleges by name (e.g. BITS Pilani, IIT Bombay, Stanford)...",
  autoNavigate = false,
  className = "",
  inputClassName = "",
  showIcon = true,
}: CollegeSearchAutocompleteProps) {
  const router = useRouter();
  const [suggestions, setSuggestions] = useState<CollegeSuggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Debounced suggestion fetching
  useEffect(() => {
    const trimmed = value.trim();
    if (trimmed.length < 1) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const results = await fetchSuggestions(trimmed, 7);
        setSuggestions(results);
        setIsOpen(results.length > 0);
      } catch (err) {
        console.error("Autocomplete error:", err);
      } finally {
        setLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [value]);

  // Click outside listener
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (college: CollegeSuggestion) => {
    onChange(college.name);
    setIsOpen(false);
    setSelectedIndex(-1);

    if (onSelect) {
      onSelect(college);
    }

    if (autoNavigate) {
      if (college.id) {
        router.push(`/colleges/${college.id}`);
      } else {
        router.push(`/search?query=${encodeURIComponent(college.name)}`);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || suggestions.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === "Enter" && selectedIndex >= 0) {
      e.preventDefault();
      handleSelect(suggestions[selectedIndex]);
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  return (
    <div ref={containerRef} className={`relative w-full ${className}`}>
      <div className="relative flex items-center w-full">
        {showIcon && (
          <div className="absolute left-3.5 text-slate-400 pointer-events-none">
            {loading ? <Loader2 className="h-4 w-4 animate-spin text-blue-600" /> : <Search className="h-4 w-4" />}
          </div>
        )}

        <input
          type="text"
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => {
            if (suggestions.length > 0) setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={`w-full text-slate-900 placeholder:text-slate-400 focus:outline-none transition ${
            showIcon ? "pl-10" : "pl-3"
          } pr-9 ${inputClassName}`}
        />

        {value && (
          <button
            type="button"
            onClick={() => {
              onChange("");
              setSuggestions([]);
              setIsOpen(false);
            }}
            className="absolute right-3 p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        )}
      </div>

      {/* Auto-suggest Dropdown */}
      {isOpen && suggestions.length > 0 && (
        <div className="absolute left-0 right-0 top-full mt-2 bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden z-50 divide-y divide-slate-100 text-left animate-in fade-in slide-in-from-top-1 duration-150">
          <div className="px-4 py-2 bg-slate-50/80 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Matching Institutions</span>
            <span>Use ↑↓ to navigate</span>
          </div>

          <div className="max-h-72 overflow-y-auto">
            {suggestions.map((item, index) => {
              const isSelected = index === selectedIndex;
              return (
                <button
                  key={item.id || item.name}
                  type="button"
                  onClick={() => handleSelect(item)}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`w-full px-4 py-3 flex items-start gap-3 transition text-left ${
                    isSelected ? "bg-blue-50/70" : "hover:bg-slate-50"
                  }`}
                >
                  <div className={`p-2 rounded-xl mt-0.5 flex-shrink-0 ${item.is_in_database ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-600"}`}>
                    <Building2 className="h-4 w-4" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-bold text-slate-900 truncate">
                        {item.name}
                      </span>
                      {item.short_name && item.short_name !== item.name && (
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600">
                          {item.short_name}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                      {(item.city || item.state) && (
                        <span className="inline-flex items-center gap-1">
                          <MapPin className="h-3 w-3 text-slate-400" />
                          {[item.city, item.state].filter(Boolean).join(", ")}
                        </span>
                      )}

                      {item.official_website && (
                        <span className="inline-flex items-center gap-1 text-slate-400 truncate max-w-[200px]">
                          <Globe className="h-3 w-3" />
                          {item.official_website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex-shrink-0 pt-1">
                    {item.is_in_database ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                        <span>In Directory</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                        <Sparkles className="h-3 w-3 text-blue-600" />
                        <span>Recognized</span>
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
