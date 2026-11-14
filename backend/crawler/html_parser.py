from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from crawler.url_extractor import URLExtractor

class HTMLParser:
    @staticmethod
    def parse_page(html_content: str, page_url: str) -> Dict[str, Any]:
        """
        Extracts structured information from raw HTML content.
        """
        soup = BeautifulSoup(html_content, "lxml")
        base_domain = URLExtractor.get_domain(page_url)

        # 1. Page Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("meta", property="og:title"):
            title = soup.find("meta", property="og:title").get("content", "").strip()

        # 2. Meta Description
        description = ""
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
        if desc_tag and desc_tag.get("content"):
            description = desc_tag["content"].strip()

        # 3. Headings
        headings: Dict[str, List[str]] = {f"h{i}": [] for i in range(1, 7)}
        for i in range(1, 7):
            for h in soup.find_all(f"h{i}"):
                text = h.get_text(strip=True)
                if text and len(text) > 1:
                    headings[f"h{i}"].append(text)

        # 4. Paragraphs
        paragraphs: List[str] = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 20: # filter out single-word snippets
                paragraphs.append(text)

        # 5. Lists
        lists: List[List[str]] = []
        for ul in soup.find_all(["ul", "ol"]):
            items = [li.get_text(strip=True) for li in ul.find_all("li") if li.get_text(strip=True)]
            if len(items) >= 2:
                lists.append(items[:100]) # ample capacity for full departmental & degree lists

        # 6. Tables
        tables: List[Dict[str, Any]] = []
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append({"headers": headers, "rows": rows[:100]})

        # 7. Links: Internal, External, and PDF
        internal_links: List[str] = []
        external_links: List[str] = []
        pdf_links: List[Dict[str, str]] = []

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            anchor_text = a.get_text(strip=True)
            norm = URLExtractor.normalize_url(href, page_url)
            if not norm:
                continue

            if URLExtractor.is_pdf(norm):
                pdf_links.append({"url": norm, "anchor_text": anchor_text or "PDF Document"})
            elif URLExtractor.is_same_or_subdomain(norm, base_domain):
                if norm not in internal_links:
                    internal_links.append(norm)
            else:
                if norm not in external_links:
                    external_links.append(norm)

        # 8. Images
        images: List[str] = []
        for img in soup.find_all("img", src=True):
            img_url = URLExtractor.normalize_url(img["src"], page_url)
            if img_url and img_url not in images:
                images.append(img_url)

        # 9. Publication / Modification Dates
        published_date = None
        date_meta = soup.find("meta", attrs={"name": re.compile(r"date|publish", re.I)}) or \
                    soup.find("meta", property=re.compile(r"published_time|modified_time", re.I))
        if date_meta and date_meta.get("content"):
            published_date = date_meta["content"].strip()

        # 10. Clean Full Text (for classification and NLP extraction)
        # Remove script and style elements
        for script_or_style in soup(["script", "style", "noscript", "svg", "header", "footer"]):
            script_or_style.decompose()

        cleaned_text = re.sub(r"\s+", " ", soup.get_text()).strip()

        return {
            "url": page_url,
            "title": title,
            "meta_description": description,
            "headings": headings,
            "paragraphs": paragraphs,
            "lists": lists,
            "tables": tables,
            "internal_links": internal_links,
            "external_links": external_links,
            "pdf_links": pdf_links,
            "images": images,
            "published_date": published_date,
            "cleaned_text": cleaned_text
        }
