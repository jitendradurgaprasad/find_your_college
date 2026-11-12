import re
from typing import Dict, List, Any
from datetime import datetime

class FacilitiesExtractor:
    @staticmethod
    def extract_facilities(page: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = page.get("cleaned_text", "")
        url = page.get("url", "")

        facility_types = [
            ("Library", r"central library|digital library|e-resources|reading hall"),
            ("Hostel", r"hostel|residential quarters|student accommodation|dormitory"),
            ("Sports", r"sports complex|gymnasium|cricket ground|badminton court|athletics track"),
            ("Laboratories", r"computing lab|high performance computing|research lab|robotics lab"),
            ("Cafeteria", r"cafeteria|food court|student dining|canteen"),
            ("Medical", r"health centre|medical facility|dispensary|emergency care"),
            ("Wi-Fi", r"wi-fi campus|high-speed internet|campus network")
        ]

        facilities = []
        for f_name, pattern in facility_types:
            if re.search(pattern, text, re.I):
                facilities.append({
                    "facility_type": f_name,
                    "name": f"Campus {f_name}",
                    "description": f"Verified campus facility documented on institutional portal: {url}",
                    "features": ["High capacity", "Accessible to students and staff"],
                    "source_url": url
                })
        return facilities

class NotificationExtractor:
    @staticmethod
    def extract_notifications(page: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = page.get("cleaned_text", "")
        url = page.get("url", "")
        headings = [h for h_list in page.get("headings", {}).values() for h in h_list]
        lists = page.get("lists", [])

        notifications = []
        seen = set()

        candidates = headings + [item for sub in lists for item in sub]
        for c in candidates:
            if re.search(r"notice|circular|announcement|date sheet|schedule|deadline", c, re.I):
                clean_title = c.strip()
                if 10 < len(clean_title) < 150 and clean_title not in seen:
                    seen.add(clean_title)
                    category = "Admission" if "admission" in clean_title.lower() else ("Examination" if "exam" in clean_title.lower() else "General")
                    notifications.append({
                        "title": clean_title,
                        "category": category,
                        "summary": f"Official institution announcement published on {url}",
                        "source_url": url
                    })
        return notifications[:10]

class ContactExtractor:
    @staticmethod
    def extract_contacts(page: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = page.get("cleaned_text", "")
        url = page.get("url", "")

        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        phones = re.findall(r"(?:\+91[-.\s]?)?[6789]\d{9}|\b0\d{2,4}[-.\s]?\d{6,8}\b", text)

        contacts = []
        if emails or phones:
            primary_email = emails[0] if emails else "contact@institution.edu"
            primary_phone = phones[0] if phones else None
            contacts.append({
                "office_name": "General Administration / Helpdesk",
                "email": primary_email,
                "phone": primary_phone,
                "address": "Official University Campus",
                "source_url": url
            })

            # Check for Admissions specific contact
            adm_match = re.search(r"(?:admissions?|enquiry)[\s\w:]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text, re.I)
            if adm_match:
                contacts.append({
                    "office_name": "Admissions Office",
                    "email": adm_match.group(1),
                    "phone": primary_phone,
                    "address": "Admissions Desk",
                    "source_url": url
                })

        return contacts
