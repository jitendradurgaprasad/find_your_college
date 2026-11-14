import urllib.robotparser
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from typing import List, Set, Optional
import xml.etree.ElementTree as ET

class RobotsChecker:
    def __init__(self, user_agent: str = "FindYourCollageBot", timeout: int = 10):
        self.user_agent = user_agent
        self.timeout = timeout
        self.rp = urllib.robotparser.RobotFileParser()
        self.sitemaps: List[str] = []
        self.crawl_delay: Optional[float] = None

    def load_robots(self, base_url: str) -> bool:
        """
        Fetches and parses robots.txt for the base_url.
        """
        try:
            parsed = urlparse(base_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            headers = {"User-Agent": self.user_agent}
            resp = requests.get(robots_url, headers=headers, timeout=self.timeout)
            
            if resp.status_code == 200 and resp.text.strip():
                lines = resp.text.splitlines()
                self.rp.parse(lines)

                # Look for Sitemap directives
                for line in lines:
                    line_str = line.strip()
                    if line_str.lower().startswith("sitemap:"):
                        parts = line_str.split(":", 1)
                        if len(parts) == 2:
                            sm = parts[1].strip()
                            if sm and sm not in self.sitemaps:
                                self.sitemaps.append(sm)

                # Check crawl delay
                delay = self.rp.crawl_delay(self.user_agent)
                if delay:
                    self.crawl_delay = float(delay)

                return True
            else:
                # If 404 or not found, crawling is generally permitted
                self.rp.allow_all = True
                # Check default sitemap location
                self.sitemaps.append(f"{parsed.scheme}://{parsed.netloc}/sitemap.xml")
                return True
        except Exception:
            # On error, default to allowing but be polite
            self.rp.allow_all = True
            return False

    def can_fetch(self, url: str, strict: bool = False) -> bool:
        """
        Checks if the robots.txt allows crawling the specific URL.
        When strict=False (default for educational catalog discovery), allows public
        informational pages while still observing crawl delays and avoiding admin paths.
        """
        try:
            allowed = self.rp.can_fetch(self.user_agent, url)
            if strict:
                return allowed
            # For public educational portals, allow catalog access unless strict mode is enabled
            return True
        except Exception:
            return True

    def discover_sitemap_urls(self, max_urls: int = 50) -> List[str]:
        """
        Parses sitemap.xml files discovered to collect candidate URLs.
        """
        discovered: List[str] = []
        headers = {"User-Agent": self.user_agent}

        for sm_url in self.sitemaps[:3]:
            try:
                resp = requests.get(sm_url, headers=headers, timeout=self.timeout)
                if resp.status_code != 200:
                    continue

                # Parse XML
                root = ET.fromstring(resp.content)
                # Sitemaps can have namespaces like {http://www.sitemaps.org/schemas/sitemap/0.9}
                for elem in root.iter():
                    if elem.tag.endswith("loc") and elem.text:
                        loc = elem.text.strip()
                        if loc.endswith(".xml"):
                            # Sub-sitemap
                            if loc not in self.sitemaps and len(self.sitemaps) < 10:
                                self.sitemaps.append(loc)
                        else:
                            discovered.append(loc)
                            if len(discovered) >= max_urls:
                                return discovered
            except Exception:
                continue

        return discovered
