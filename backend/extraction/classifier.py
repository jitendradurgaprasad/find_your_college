import re
from typing import List, Dict, Any, Set

CATEGORY_PATTERNS = {
    "ADMISSIONS": [
        r"admission", r"apply-now", r"admissions", r"eligibility", r"counselling",
        r"entrance-exam", r"seat-allotment", r"cut-off", r"how-to-apply", r"intake"
    ],
    "COURSES": [
        r"course", r"program", r"academics", r"curriculum", r"syllabus",
        r"degree", r"btech", r"mtech", r"undergraduate", r"postgraduate", r"phd"
    ],
    "SCHOLARSHIPS": [
        r"scholarship", r"financial-aid", r"fellowship", r"stipend", r"fee-waiver",
        r"grant", r"endowment"
    ],
    "FACULTY": [
        r"faculty", r"professor", r"staff", r"directory", r"dean", r"people",
        r"instructors", r"teaching-staff"
    ],
    "PLACEMENTS": [
        r"placement", r"career", r"recruitment", r"campus-drive", r"internship",
        r"highest-package", r"job-offers", r"training-and-placement"
    ],
    "FACILITIES": [
        r"campus", r"facility", r"infrastructure", r"hostel", r"library",
        r"sports", r"laboratory", r"transport", r"cafeteria", r"mess"
    ],
    "RESEARCH": [
        r"research", r"publication", r"patent", r"laboratory", r"innovation",
        r"center-of-excellence", r"funded-project"
    ],
    "NOTIFICATIONS": [
        r"notification", r"announcement", r"circular", r"news", r"events",
        r"notice-board", r"latest-updates"
    ],
    "CONTACT": [
        r"contact", r"reach-us", r"about-us", r"administration", r"directory",
        r"leadership", r"registrar"
    ]
}

class ContentClassifier:
    @staticmethod
    def classify_page(page: Dict[str, Any]) -> List[str]:
        """
        Classifies a crawled page into one or more categories based on URL path,
        title, headings, and clean text keywords.
        """
        url = page.get("url", "").lower()
        title = page.get("title", "").lower()
        headings = " ".join([h.lower() for h_list in page.get("headings", {}).values() for h in h_list])
        text_snippet = page.get("cleaned_text", "")[:2000].lower()

        combined_text = f"{url} {title} {headings} {text_snippet}"
        categories: List[str] = []

        for category, patterns in CATEGORY_PATTERNS.items():
            score = 0
            for pattern in patterns:
                # Strong weight for URL path match
                if re.search(pattern, url):
                    score += 3
                # Weight for title match
                if re.search(r"\b" + pattern, title):
                    score += 2
                # Weight for headings match
                if re.search(r"\b" + pattern, headings):
                    score += 2
                # Basic weight for body match
                if re.search(r"\b" + pattern, text_snippet):
                    score += 1

            if score >= 3:
                categories.append(category)

        # Default fallback
        if not categories:
            categories.append("GENERAL")

        return categories
