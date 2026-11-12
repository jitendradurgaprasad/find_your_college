import io
from typing import Dict, Any, Optional
import requests
from pypdf import PdfReader
from crawler.url_extractor import URLExtractor

class PDFParser:
    @staticmethod
    def extract_from_url(pdf_url: str, max_pages: int = 20, timeout: int = 15) -> Dict[str, Any]:
        """
        Downloads and extracts clean text and metadata from a PDF URL.
        """
        if not URLExtractor.is_ssrf_safe(pdf_url):
            return {"error": "SSRF check failed: restricted URL", "text": "", "page_count": 0}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FindYourCollageBot/1.0"
        }

        try:
            # Stream with size limit (max 15MB)
            resp = requests.get(pdf_url, headers=headers, stream=True, timeout=timeout)
            if resp.status_code != 200:
                return {"error": f"HTTP status {resp.status_code}", "text": "", "page_count": 0}

            content_len = resp.headers.get("Content-Length")
            if content_len and int(content_len) > 15 * 1024 * 1024:
                return {"error": "PDF file size exceeds 15MB limit", "text": "", "page_count": 0}

            data = io.BytesIO()
            total_downloaded = 0
            for chunk in resp.iter_content(chunk_size=65536):
                data.write(chunk)
                total_downloaded += len(chunk)
                if total_downloaded > 15 * 1024 * 1024:
                    return {"error": "PDF exceeded size limit during download", "text": "", "page_count": 0}

            data.seek(0)
            return PDFParser.extract_from_bytes(data.read(), pdf_url, max_pages)

        except Exception as e:
            return {"error": str(e), "text": "", "page_count": 0}

    @staticmethod
    def extract_from_bytes(pdf_bytes: bytes, source_url: str = "", max_pages: int = 20) -> Dict[str, Any]:
        """
        Extracts text from raw PDF bytes.
        """
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(reader.pages)
            pages_to_extract = min(total_pages, max_pages)

            text_chunks = []
            for i in range(pages_to_extract):
                try:
                    page = reader.pages[i]
                    extracted = page.extract_text()
                    if extracted:
                        text_chunks.append(extracted.strip())
                except Exception:
                    continue

            full_text = "\n\n".join(text_chunks)
            meta = reader.metadata or {}

            return {
                "source_url": source_url,
                "title": str(meta.get("/Title", "") or ""),
                "author": str(meta.get("/Author", "") or ""),
                "page_count": total_pages,
                "pages_extracted": pages_to_extract,
                "text": full_text
            }
        except Exception as e:
            return {"error": f"Failed to parse PDF: {str(e)}", "text": "", "page_count": 0}
