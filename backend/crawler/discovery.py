import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import requests
from app.config import settings
from crawler.url_extractor import URLExtractor

KNOWN_AGGREGATORS = [
    "shiksha.com", "collegedunia.com", "careers360.com", "getmyuni.com",
    "jagranjosh.com", "wikipedia.org", "facebook.com", "instagram.com",
    "linkedin.com", "twitter.com", "youtube.com", "reddit.com", "quora.com"
]

class DiscoveryEngine:
    def __init__(self, api_key: Optional[str] = None, provider: Optional[str] = None):
        self.api_key = api_key or settings.SEARCH_API_KEY
        self.provider = (provider or settings.SEARCH_PROVIDER).lower()

    def discover_institutions(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Discovers educational institutions matching the query via Tavily, Brave, or direct search.
        Filters out commercial aggregators and prioritizes official educational domains.
        """
        if not self.api_key:
            return []

        if self.provider == "tavily":
            return self._search_tavily(query, max_results)
        elif self.provider == "brave":
            return self._search_brave(query, max_results)
        else:
            return []

    def _search_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": f"{query} official website university college admission",
            "search_depth": "advanced",
            "include_domains": [],
            "exclude_domains": KNOWN_AGGREGATORS,
            "max_results": max_results * 2
        }

        try:
            resp = requests.post(url, json=payload, timeout=12)
            if resp.status_code != 200:
                return []

            data = resp.json()
            raw_results = data.get("results", [])
            return self._process_search_results(raw_results)
        except Exception:
            return []

    def _search_brave(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        params = {"q": f"{query} official website", "count": max_results * 2}

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=12)
            if resp.status_code != 200:
                return []

            data = resp.json()
            web = data.get("web", {})
            raw_results = web.get("results", [])
            return self._process_search_results(raw_results)
        except Exception:
            return []

    def _process_search_results(self, raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicates domains, prioritizes educational domains, and checks basic URL accessibility.
        """
        seen_domains = set()
        institutions: List[Dict[str, Any]] = []

        for item in raw_items:
            url = item.get("url", "")
            title = item.get("title", "")
            snippet = item.get("content", "") or item.get("description", "")

            norm_url = URLExtractor.normalize_url(url)
            if not norm_url:
                continue

            domain = URLExtractor.get_domain(norm_url)
            if not domain or domain in seen_domains:
                continue

            # Skip aggregators
            if any(agg in domain for agg in KNOWN_AGGREGATORS):
                continue

            seen_domains.add(domain)

            # Score officialness
            is_edu = any(domain.endswith(tld) for tld in [".edu", ".ac.in", ".edu.in", ".ac.uk", ".edu.au", ".ernet.in", ".org"])
            
            clean_name = self._extract_institution_name(title, domain)

            institutions.append({
                "name": clean_name,
                "official_website": norm_url,
                "domain": domain,
                "snippet": snippet,
                "is_official_domain": is_edu,
                "source": "Search Discovery"
            })

        # Sort official educational domains first
        institutions.sort(key=lambda x: (x["is_official_domain"]), reverse=True)
        return institutions

    def _extract_institution_name(self, title: str, domain: str) -> str:
        """
        Cleans search result titles to obtain the college/university name.
        """
        cleaned = re.split(r"[-|:|–|—|•]", title)[0].strip()
        cleaned = re.sub(r"(Official Website|Home|Welcome to|Admissions).*$", "", cleaned, flags=re.I).strip()
        if len(cleaned) < 4:
            cleaned = domain.replace(".ac.in", "").replace(".edu.in", "").replace(".edu", "").replace(".org", "").title()
        return cleaned

    @staticmethod
    def verify_url_accessible(url: str, timeout: int = 8) -> bool:
        """
        Verifies that discovered URL is genuinely reachable and responds with 2xx/3xx.
        """
        if not URLExtractor.is_ssrf_safe(url):
            return False

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FindYourCollageBot/1.0"
        }
        try:
            resp = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            return resp.status_code < 400
        except Exception:
            try:
                resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
                return resp.status_code < 400
            except Exception:
                return False
