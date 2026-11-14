import ipaddress
import socket
from urllib.parse import urlparse, urljoin, urldefrag
from typing import Optional, Set, List
import re

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"), # Link-local / AWS/GCP/Azure metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10")
]

class URLExtractor:
    @staticmethod
    def is_ssrf_safe(url: str) -> bool:
        """
        Validates that a URL does not resolve to private IPs, localhost, or cloud metadata.
        Crucial SSRF protection required by Section 15.
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False

            hostname = parsed.hostname
            if not hostname:
                return False

            # Check direct localhost
            if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "metadata.google.internal"):
                return False

            # Resolve DNS
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                for network in BLOCKED_IP_NETWORKS:
                    if ip_obj in network:
                        return False

            return True
        except Exception:
            return False

    @staticmethod
    def normalize_url(raw_url: str, base_url: Optional[str] = None) -> Optional[str]:
        """
        Cleans URL, removes fragments, resolves relative URLs, and validates scheme.
        """
        try:
            raw_url = raw_url.strip()
            if not raw_url or raw_url.startswith(("javascript:", "mailto:", "tel:", "#", "data:")):
                return None

            if base_url:
                joined = urljoin(base_url, raw_url)
            else:
                joined = raw_url

            clean_url, _ = urldefrag(joined)
            parsed = urlparse(clean_url)

            if parsed.scheme not in ("http", "https"):
                return None

            # Lowercase hostname and scheme
            netloc = parsed.netloc.lower()
            path = parsed.path or "/"

            # Normalize double slashes in path
            path = re.sub(r"/+", "/", path)

            normalized = f"{parsed.scheme}://{netloc}{path}"
            if parsed.query:
                normalized += f"?{parsed.query}"

            return normalized
        except Exception:
            return None

    @staticmethod
    def get_domain(url: str) -> str:
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            if ":" in netloc:
                netloc = netloc.split(":")[0]
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc
        except Exception:
            return ""

    @staticmethod
    def is_safe_public_path(url: str) -> bool:
        """
        Ensures the crawler accesses public academic and informational pages while
        strictly skipping private, backend, login, or administrative endpoints.
        """
        clean = url.lower()
        blocked_subpaths = [
            "/wp-admin", "/wp-login", "/cgi-bin", "/admin/", "/administrator/",
            "/cpanel", "/webmail", "/cart", "/checkout", "/session", "/install",
            "/update.php", "/xmlrpc.php", "/login", "/signin", "/auth/",
            "/user/login", "/member/login", "/student-login", "/staff-login"
        ]
        return not any(bp in clean for bp in blocked_subpaths)

    @staticmethod
    def score_academic_url(url: str, anchor_text: str = "") -> int:
        """
        Computes an academic priority score for link prioritization in the crawler engine.
        Ensures high-yield course, admission, fee, faculty, and degree pages are crawled first.
        """
        score = 0
        combined = f"{url.lower()} {anchor_text.lower()}"

        # Tier 1: Highest Priority Academic Core (+90 to +120)
        core_patterns = [
            ("academic-program", 130), ("ug_pg", 130), ("btech", 125), ("mtech", 120),
            ("shms", 120), ("soet", 120), ("course", 110), ("program", 110),
            ("academic", 100), ("admission-procedure", 115), ("admission-process", 115),
            ("admission", 100), ("fee-structure", 115), ("fee", 95), ("tuition", 95),
            ("prospectus", 105), ("placement", 105), ("career", 90),
            ("scholarship", 100), ("faculty-staff", 100), ("faculty_directory", 100),
            ("faculty", 90), ("bca", 95), ("mca", 95), ("mba", 100), ("bba", 90),
            ("b.sc", 90), ("m.sc", 90), ("phd", 95), ("ph.d", 95), ("doctoral", 95),
            ("allied", 100), ("health", 90), ("nursing", 95), ("pharmacy", 95),
            ("medical", 95), ("physiotherapy", 95), ("bpt", 95), ("mpt", 95),
            ("department", 85), ("curriculum", 90), ("syllabus", 85), ("school", 80),
            ("degree", 85), ("eligibility", 90), ("intake", 90), ("seat", 85)
        ]
        for kw, pts in core_patterns:
            if kw in combined:
                score += pts

        # Tier 2: Campus, Facilities & General Context (+20 to +40)
        medium_patterns = [
            ("campus", 30), ("facility", 30), ("facilities", 30), ("hostel", 30),
            ("library", 35), ("research", 40), ("laboratory", 30),
            ("accreditation", 25), ("ranking", 25), ("about", 15), ("overview", 15)
        ]
        for kw, pts in medium_patterns:
            if kw in combined:
                score += pts

        # Tier 3: Deprioritized / Non-Academic Administration (-30 to -80)
        deprioritized_patterns = [
            ("president", -60), ("chancellor", -60), ("vice_chancellor", -60),
            ("governing", -50), ("committee", -50), ("statute", -60), ("act-statutes", -70),
            ("sedg", -50), ("rti", -60), ("tender", -70), ("gallery", -50),
            ("photo", -40), ("video", -40), ("alumni", -40), ("newsletter", -40),
            ("login", -90), ("signin", -90), ("portal", -70), ("auth", -90)
        ]
        for kw, pts in deprioritized_patterns:
            if kw in combined:
                score += pts

        return score

    @staticmethod
    def is_same_or_subdomain(url: str, base_domain: str) -> bool:
        """
        Checks if url belongs to the same domain or subdomains of base_domain.
        """
        domain = URLExtractor.get_domain(url)
        base = base_domain.lower()
        if base.startswith("www."):
            base = base[4:]
        return domain == base or domain.endswith("." + base)

    @staticmethod
    def is_pdf(url: str) -> bool:
        clean = url.lower().split("?")[0]
        return clean.endswith(".pdf")
