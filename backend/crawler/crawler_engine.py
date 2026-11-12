import hashlib
import time
import requests
from collections import deque
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
        max_pages: int = 30,
        request_delay: float = 0.8,
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
        Executes a controlled, respectful, depth-limited breadth-first crawl of an institutional site.
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
        self.log("INFO", f"Starting crawler for domain: {base_domain} (Seed: {norm_seed})")

        # 2. Robots.txt and Sitemap discovery
        robots = RobotsChecker(user_agent=settings.USER_AGENT, timeout=self.timeout)
        self.log("INFO", f"Checking robots.txt and sitemap permissions on {base_domain}...")
        robots.load_robots(norm_seed)

        if not robots.can_fetch(norm_seed):
            self.log("WARNING", f"Robots.txt disallows crawling seed URL {norm_seed}")
            return {"status": "FAILED", "error": "Seed URL blocked by site robots.txt policy"}

        # 3. Queue Initialization
        queue = deque([(norm_seed, 0, None)]) # (url, depth, parent_url)
        self.visited_urls.add(norm_seed)

        # Attempt sitemap seed injection for important pages
        sitemap_urls = robots.discover_sitemap_urls(max_urls=15)
        if sitemap_urls:
            self.log("INFO", f"Discovered {len(sitemap_urls)} URLs from sitemap.xml")
            for sm_url in sitemap_urls:
                norm_sm = URLExtractor.normalize_url(sm_url)
                if norm_sm and URLExtractor.is_same_or_subdomain(norm_sm, base_domain) and norm_sm not in self.visited_urls:
                    if robots.can_fetch(norm_sm):
                        queue.append((norm_sm, 1, norm_seed))
                        self.visited_urls.add(norm_sm)

        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        pages_crawled_count = 0

        # 4. Crawl Loop
        while queue and pages_crawled_count < self.max_pages:
            current_url, depth, parent_url = queue.popleft()

            # Respect robots.txt
            if not robots.can_fetch(current_url):
                self.log("WARNING", f"Skipping {current_url} (blocked by robots.txt)")
                continue

            # Respect crawl delay
            delay = robots.crawl_delay or self.request_delay
            time.sleep(delay)

            try:
                self.log("INFO", f"Fetching [{pages_crawled_count + 1}/{self.max_pages}] (Depth {depth}): {current_url}")
                resp = requests.get(current_url, headers=headers, timeout=self.timeout)

                if resp.status_code != 200:
                    self.failed_urls.append({"url": current_url, "error": f"HTTP {resp.status_code}"})
                    self.log("WARNING", f"HTTP {resp.status_code} on {current_url}")
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

                # Discover new links if depth allows
                if depth < self.max_depth:
                    for link in parsed_data["internal_links"]:
                        if link not in self.visited_urls and len(self.visited_urls) < (self.max_pages * 3):
                            self.visited_urls.add(link)
                            queue.append((link, depth + 1, current_url))

            except Exception as e:
                self.failed_urls.append({"url": current_url, "error": str(e)})
                self.log("ERROR", f"Error fetching {current_url}: {str(e)}")

        duration = time.time() - start_time
        self.log("SUCCESS", f"Crawl finished. Crawled {pages_crawled_count} pages in {duration:.2f}s.")

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
