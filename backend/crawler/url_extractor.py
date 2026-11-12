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
