import json
import os
import time
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

import models

load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GeminiDisabilityGrouper:
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key or os.getenv("PUBLIC_GROQ_API_KEY")
        self.model = model
        if not self.api_key:
            print("[Groq] GROQ_API_KEY not set — using fallback grouping.")

    def group_disabilities(self, disabilities: List[str]) -> List[dict]:
        if not disabilities:
            return []
        if not self.api_key:
            return self._fallback_groups(disabilities)
        try:
            prompt = "\n".join(
                [
                    "Group the following disability labels by semantic similarity.",
                    "Each item must appear exactly once.",
                    "Do not add new items.",
                    "Keep groups practical (e.g., visual, hearing, mobility, cognitive).",
                    "Return ONLY valid JSON, no markdown, no backticks, in this format:",
                    '{"groups":[{"label":"string","items":["string"]}]}',
                    "",
                    "Input:",
                    *[f"- {d}" for d in disabilities],
                ]
            )

            body = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 1024,
            }
            resp = requests.post(
                GROQ_API_URL,
                json=body,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            resp.raise_for_status()

            data = resp.json()
            text = data["choices"][0]["message"]["content"]

            parsed = json.loads(text)
            print(parsed)
            groups = parsed.get("groups", [])
            print(f"[Gemini] Grouped {len(disabilities)} disabilities into {len(groups)} groups.")
            return groups if isinstance(groups, list) else self._fallback_groups(disabilities)
        except Exception as e:
            print(f"[Gemini] API call failed: {e} — using fallback grouping.")
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

    # Only cache if Gemini actually responded (mapping is non-empty or disabilities is empty)
    if mapping or not disabilities:
        _GROUP_CACHE["map"] = mapping
        _GROUP_CACHE["expires_at"] = now + ttl_seconds
    else:
        # Gemini failed/fell back — retry on next request instead of caching empty/fallback result
        _GROUP_CACHE["map"] = mapping  # still use it for this request
        _GROUP_CACHE["expires_at"] = now + 5  # but expire in 5s so we retry soon
        print("[Gemini] Fallback result not cached long-term — will retry in 5s.")

    return mapping

def compute_group_ratings(
    review_rows: List[Tuple[models.Review, Optional[str]]],
    disability_to_group: Dict[str, str],
) -> Dict[str, float]:
    buckets: Dict[str, List[int]] = {}
    for review, disability in review_rows:
        d = (disability or "").strip()
        group = disability_to_group.get(d, "Other")
        buckets.setdefault(group, []).append(int(review.rating))

    return {
        label: round(sum(ratings) / len(ratings), 2)
        for label, ratings in sorted(buckets.items(), key=lambda kv: kv[0].lower())
    }