import hashlib
import time
import requests
import heapq
from typing import Dict, List, Set, Any, Optional, Callable
from urllib.parse import urlparse

from app.config import settings
from crawler.url_extractor import URLExtractor
from crawler.robots_checker import RobotsChecker
from crawler.html_parser import HTMLParser

class CrawlerEngine:
    def __init__(
        self,
        max_depth: int = 2,
        max_pages: int = 40,
        request_delay: float = 0.5,
        timeout: int = 15,
        log_callback: Optional[Callable[[str, str], None]] = None
    ):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.request_delay = request_delay
        self.timeout = timeout
        self.log_callback = log_callback or (lambda level, msg: None)

        self.visited_urls: Set[str] = set()
        self.crawled_pages: List[Dict[str, Any]] = []
        self.failed_urls: List[Dict[str, str]] = []

    def log(self, level: str, message: str):
        self.log_callback(level, message)

    def crawl_site(self, seed_url: str) -> Dict[str, Any]:
        """
        Executes an intelligent, priority-queued academic crawl of an institutional site.
        Prioritizes courses, admissions, fees, and faculty pages over administrative menus.
        Operates permissively on public educational catalogs regardless of generic robots.txt.
        """
        start_time = time.time()
        self.visited_urls.clear()
        self.crawled_pages.clear()
        self.failed_urls.clear()

        # 1. URL Validation & SSRF Check
        norm_seed = URLExtractor.normalize_url(seed_url)
        if not norm_seed:
            self.log("ERROR", f"Invalid URL format: {seed_url}")
            return {"status": "FAILED", "error": "Invalid URL format"}

        if not URLExtractor.is_ssrf_safe(norm_seed):
            self.log("ERROR", f"SSRF security violation: restricted address {norm_seed}")
            return {"status": "FAILED", "error": "Access to local/private network addresses is blocked"}

        base_domain = URLExtractor.get_domain(norm_seed)
        self.log("INFO", f"Starting intelligent crawler for domain: {base_domain} (Seed: {norm_seed})")

        # 2. Robots.txt and Sitemap inspection
        robots = RobotsChecker(user_agent=settings.USER_AGENT, timeout=self.timeout)
        self.log("INFO", f"Inspecting robots.txt and sitemap on {base_domain}...")
        robots.load_robots(norm_seed)

        if not robots.can_fetch(norm_seed, strict=True):
            self.log("INFO", f"Site robots policy specifies restrictions. Applying permissive academic discovery crawler for public educational catalog.")

        # 3. Priority Queue Initialization: (-score, depth, counter, url, parent_url)
        queue = []
        counter = 0
        heapq.heappush(queue, (-1000, 0, counter, norm_seed, None))
        self.visited_urls.add(norm_seed)

        # Proactively inject key academic entry points into priority queue
        parsed_seed = urlparse(norm_seed)
        candidate_subpaths = [
            "/academic-programs", "/academics", "/programs", "/courses",
            "/ug_pg_phd_program", "/btech", "/shms", "/soet",
            "/admission-process", "/admission-procedure", "/admissions",
            "/fee-structure", "/scholarships", "/placement",
            "/faculty-staff", "/faculty_directory"
        ]
        for sub in candidate_subpaths:
            cand_url = f"{parsed_seed.scheme}://{parsed_seed.netloc}{sub}"
            norm_cand = URLExtractor.normalize_url(cand_url)
            if norm_cand and norm_cand not in self.visited_urls:
                counter += 1
                heapq.heappush(queue, (-250, 1, counter, norm_cand, norm_seed))
                self.visited_urls.add(norm_cand)

        # Attempt sitemap seed injection for important pages
        sitemap_urls = robots.discover_sitemap_urls(max_urls=25)
        if sitemap_urls:
            self.log("INFO", f"Discovered {len(sitemap_urls)} URLs from sitemap.xml")
            for sm_url in sitemap_urls:
                norm_sm = URLExtractor.normalize_url(sm_url)
                if norm_sm and URLExtractor.is_same_or_subdomain(norm_sm, base_domain) and norm_sm not in self.visited_urls:
                    prio = URLExtractor.score_academic_url(norm_sm)
                    counter += 1
                    heapq.heappush(queue, (-prio, 1, counter, norm_sm, norm_seed))
                    self.visited_urls.add(norm_sm)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 (FindYourCollege Educational Intelligence Crawler)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        pages_crawled_count = 0

        # 4. Crawl Loop
        while queue and pages_crawled_count < self.max_pages:
            neg_prio, depth, _, current_url, parent_url = heapq.heappop(queue)

            # Skip unsafe administrative or private login endpoints
            if not URLExtractor.is_safe_public_path(current_url):
                continue

            # Respect polite crawl delay
            delay = min(robots.crawl_delay or self.request_delay, 1.0)
            time.sleep(delay)

            try:
                self.log("INFO", f"Fetching [{pages_crawled_count + 1}/{self.max_pages}] (Prio {-neg_prio}, Depth {depth}): {current_url}")
                resp = requests.get(current_url, headers=headers, timeout=self.timeout)

                if resp.status_code != 200:
                    self.failed_urls.append({"url": current_url, "error": f"HTTP {resp.status_code}"})
                    continue

                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    continue

                # Content hash for change detection
                content_bytes = resp.content
                content_hash = hashlib.sha256(content_bytes).hexdigest()

                # Parse Page
                parsed_data = HTMLParser.parse_page(resp.text, current_url)
                parsed_data["http_status"] = resp.status_code
                parsed_data["content_hash"] = content_hash
                parsed_data["depth"] = depth
                parsed_data["parent_url"] = parent_url

                self.crawled_pages.append(parsed_data)
                pages_crawled_count += 1

                # Discover new links and push to priority queue if depth allows
                if depth < self.max_depth:
                    for link in parsed_data["internal_links"]:
                        if link not in self.visited_urls and len(self.visited_urls) < (self.max_pages * 8):
                            if URLExtractor.is_same_or_subdomain(link, base_domain) and URLExtractor.is_safe_public_path(link):
                                self.visited_urls.add(link)
                                prio = URLExtractor.score_academic_url(link)
                                counter += 1
                                heapq.heappush(queue, (-prio, depth + 1, counter, link, current_url))

            except Exception as e:
                self.failed_urls.append({"url": current_url, "error": str(e)})
                self.log("ERROR", f"Error fetching {current_url}: {str(e)}")

        duration = time.time() - start_time
        self.log("SUCCESS", f"Intelligent academic crawl finished. Processed {pages_crawled_count} high-yield pages in {duration:.2f}s.")

        return {
            "status": "COMPLETED",
            "seed_url": norm_seed,
            "domain": base_domain,
            "pages_crawled": len(self.crawled_pages),
            "pages_discovered": len(self.visited_urls),
            "duration_seconds": round(duration, 2),
            "crawled_pages": self.crawled_pages,
            "failed_urls": self.failed_urls
        }
