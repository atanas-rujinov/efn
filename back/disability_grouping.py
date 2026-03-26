import json
import os
import time
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

import models

try:
    from google import genai
except Exception:
    genai = None


class GeminiDisabilityGrouper:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.client = genai.Client(api_key=self.api_key) if (genai and self.api_key) else None

    def group_disabilities(self, disabilities: List[str]) -> List[dict]:
        if not disabilities:
            return []
        if not self.client:
            return self._fallback_groups(disabilities)
        try:
            prompt = "\n".join(
                [
                    "Group the following disability labels by semantic similarity.",
                    "Each item must appear exactly once.",
                    "Do not add new items.",
                    "Keep groups practical (e.g., visual, hearing, mobility, cognitive).",
                    "Return ONLY JSON in this format:",
                    '{"groups":[{"label":"string","items":["string"]}]}',
                    "",
                    "Input:",
                    *[f"- {d}" for d in disabilities],
                ]
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"response_mime_type": "application/json", "temperature": 0},
            )
            parsed = json.loads(response.text)
            groups = parsed.get("groups", [])
            return groups if isinstance(groups, list) else self._fallback_groups(disabilities)
        except Exception:
            # Quota/network/model failures should never break the profile endpoint.
            return self._fallback_groups(disabilities)

    def _fallback_groups(self, disabilities: List[str]) -> List[dict]:
        buckets: Dict[str, List[str]] = {
            "Visual": [],
            "Hearing": [],
            "Mobility": [],
            "Cognitive / Neurodivergent": [],
            "Speech / Communication": [],
            "Chronic / Medical": [],
            "Other": [],
        }
        for item in disabilities:
            v = item.lower()
            if any(k in v for k in ["blind", "vision", "visual", "sight"]):
                buckets["Visual"].append(item)
            elif any(k in v for k in ["deaf", "hearing", "hard of hearing"]):
                buckets["Hearing"].append(item)
            elif any(k in v for k in ["wheelchair", "mobility", "walk", "paral", "amput"]):
                buckets["Mobility"].append(item)
            elif any(k in v for k in ["autis", "adhd", "dyslex", "cognit", "intellect", "memory"]):
                buckets["Cognitive / Neurodivergent"].append(item)
            elif any(k in v for k in ["speech", "stutter", "communicat"]):
                buckets["Speech / Communication"].append(item)
            elif any(k in v for k in ["chronic", "pain", "epilep", "diabet", "medical"]):
                buckets["Chronic / Medical"].append(item)
            else:
                buckets["Other"].append(item)
        return [{"label": label, "items": items} for label, items in buckets.items() if items]


_GROUP_CACHE: Dict[str, object] = {"expires_at": 0.0, "map": {}}


def get_disability_to_group_map(db: Session, ttl_seconds: int = 900) -> Dict[str, str]:
    now = time.time()
    if _GROUP_CACHE["map"] and now < float(_GROUP_CACHE["expires_at"]):
        return _GROUP_CACHE["map"]  # type: ignore[return-value]

    rows = (
        db.query(models.Disabled.disability)
        .filter(models.Disabled.disability.isnot(None))
        .all()
    )
    disabilities = sorted({(r[0] or "").strip() for r in rows if (r[0] or "").strip()})

    grouper = GeminiDisabilityGrouper()
    groups = grouper.group_disabilities(disabilities)
    mapping: Dict[str, str] = {}
    for g in groups:
        label = str(g.get("label", "Other")).strip() or "Other"
        for item in g.get("items", []):
            key = str(item).strip()
            if key:
                mapping[key] = label

    _GROUP_CACHE["map"] = mapping
    _GROUP_CACHE["expires_at"] = now + ttl_seconds
    return mapping


def compute_group_ratings(
    review_rows: List[Tuple[models.Review, Optional[str]]],
    disability_to_group: Dict[str, str],
) -> List[dict]:
    buckets: Dict[str, List[int]] = {}
    for review, disability in review_rows:
        d = (disability or "").strip()
        group = disability_to_group.get(d, "Other")
        buckets.setdefault(group, []).append(int(review.rating))

    results = []
    for label, ratings in sorted(buckets.items(), key=lambda kv: kv[0].lower()):
        total = len(ratings)
        avg = round(sum(ratings) / total, 2) if total else 0.0
        results.append({"label": label, "average_rating": avg, "total_reviews": total})
    return results

