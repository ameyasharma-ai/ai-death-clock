"""Gemini AI Longevity Engine.

Orchestrates communication with Google Gemini cloud models to perform
actuarial lifespan estimation, risk decomposition, and longevity protocol generation.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import json
import re
from typing import Any
import httpx

from config import config
from models import LifespanEstimate, UserProfile


class GeminiEngine:
    """Interacts with Google Gemini models to assess biological life expectancy.

    Attributes:
        api_key: Gemini API key.
        base_url: Base endpoint URL.
        primary_model: Preferred model identifier.
        fallback_models: Ordered list of alternate models.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        primary_model: str | None = None,
        fallback_models: list[str] | None = None,
    ) -> None:
        """Initialize Gemini engine parameters.

        Args:
            api_key: Optional custom API key.
            base_url: Optional custom base URL.
            primary_model: Optional preferred model name.
            fallback_models: Optional list of fallback models.
        """
        self.api_key: str = api_key or config.gemini_api_key
        self.base_url: str = (base_url or config.gemini_base_url).rstrip("/")
        self.primary_model: str = primary_model or config.gemini_model
        self.fallback_models: list[str] = (
            fallback_models if fallback_models is not None else config.gemini_fallback_models
        )

    def _get_headers(self) -> dict[str, str]:
        """Build HTTP authorization headers.

        Returns:
            dict[str, str]: Standard headers for Gemini OpenAI-compatible gateway.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def scan_models(self) -> list[dict[str, Any]]:
        """Probe available models and benchmark response times.

        Returns:
            list[dict[str, Any]]: Model availability status and latency metrics.
        """
        results: list[dict[str, Any]] = []
        candidates = [self.primary_model] + [
            m for m in self.fallback_models if m != self.primary_model
        ]

        import time
        with httpx.Client(base_url=self.base_url, headers=self._get_headers(), timeout=12.0) as client:
            for model_name in candidates:
                start_time = time.perf_counter()
                try:
                    resp = client.post(
                        "/chat/completions",
                        json={
                            "model": model_name,
                            "messages": [{"role": "user", "content": "Ping"}],
                            "max_tokens": 5,
                        },
                    )
                    elapsed = time.perf_counter() - start_time
                    if resp.status_code == 200:
                        results.append(
                            {
                                "model": model_name,
                                "available": True,
                                "latency_s": round(elapsed, 2),
                                "error": None,
                            }
                        )
                    else:
                        results.append(
                            {
                                "model": model_name,
                                "available": False,
                                "latency_s": round(elapsed, 2),
                                "error": f"HTTP {resp.status_code}: {resp.text[:120]}",
                            }
                        )
                except Exception as exc:
                    elapsed = time.perf_counter() - start_time
                    results.append(
                        {
                            "model": model_name,
                            "available": False,
                            "latency_s": round(elapsed, 2),
                            "error": str(exc),
                        }
                    )
        return results

    def build_prompt(self, profile: UserProfile) -> str:
        """Construct a rigorous biogerontological analysis prompt.

        Args:
            profile: User lifestyle, geographic, and demographic profile.

        Returns:
            str: System and user combined instructions formatted for JSON output.
        """
        custom_text = ""
        if profile.custom_fields:
            items = [f"- {k}: {v}" for k, v in profile.custom_fields.items() if str(v).strip()]
            if items:
                custom_text = "\n[CUSTOM ATTRIBUTES & BIOMARKERS]\n" + "\n".join(items) + "\n"

        personal_text = ""
        if profile.personal_notes and profile.personal_notes.strip():
            personal_text = f"\n[PERSONAL DETAILS & UNIQUE LIFE CONTEXT]\n{profile.personal_notes.strip()}\n"

        return f"""You are an elite actuarial scientist, biogerontologist, and public health longevity modeler.
Analyze the following subject profile to calculate their estimated biological life expectancy:

[SUBJECT PROFILE]
- Birth Date: {profile.birth_date}
- Biological Sex: {profile.biological_sex}
- Country of Residence: {profile.country}
- City / Region: {profile.city}
- Living Environment: {profile.living_area}
- Air Quality / Environmental Exposure: {profile.air_quality}
- Sleep: {profile.sleep_hours} hrs/night (Quality: {profile.sleep_quality})
- Exercise: {profile.exercise_frequency}
- Nutrition / Diet: {profile.diet_type}
- Smoking / Inhalation: {profile.smoking_status}
- Alcohol: {profile.alcohol_units_per_week} drinks/week
- Daily Caffeine: {profile.caffeine_daily_cups} cups
- Stress Level (1-10): {profile.stress_level}
- Work Nature: {profile.work_nature}
- Social Connection & Tribe: {profile.social_connection}
- Sense of Purpose / Ikigai: {profile.sense_of_purpose}
- Family Longevity History: {profile.family_longevity}
- Chronic Medical Conditions: {profile.chronic_conditions}
{custom_text}{personal_text}
[TASK INSTRUCTIONS]
1. Determine the baseline national actuarial life expectancy for this sex in this country.
2. Calculate the net modifier in years based on the synergistic combination of their diet, exercise, sleep, environmental pollution, stress, social cohesion, and genetic factors.
3. Crucially analyze and factor in all personal notes, unique lifestyle habits, biomarkers, and custom details provided above (e.g. fasting, cold plunges, sauna, high-impact stress, supplements, specific ancestral lifespans).
4. Compute the final predicted lifespan in years (e.g. 84.6).
5. Provide a philosophical yet grounded scientific summary of their trajectory referencing any notable personal context they shared.
6. Identify the top 3-4 life-extending longevity boosters with estimated years added (e.g. "Optimal Sleep Quality (+2.8 yrs)").
7. Identify the top 2-3 risk dampeners with estimated years reduced (e.g. "Urban PM2.5 Pollution Exposure (-1.4 yrs)").
8. Suggest 3-4 highest-leverage, practical interventions to expand their healthspan and lifespan tailored to their personal situation.

You MUST respond strictly with a valid JSON object matching this schema:
{{
  "estimated_lifespan_years": 84.5,
  "baseline_country_expectancy": 71.0,
  "net_lifestyle_modifier_years": 13.5,
  "summary": "Concise 2-3 sentence assessment...",
  "top_boosters": [
    "Non-smoker (+4.0 yrs)",
    "Consistent resistance & aerobic training (+3.2 yrs)"
  ],
  "top_risks": [
    "Sedentary desk hours (-1.2 yrs)",
    "Air quality exposure (-1.1 yrs)"
  ],
  "longevity_recommendations": [
    "Introduce Zone 2 cardio 3x per week",
    "HEPA air purifier in home environment"
  ]
}}
"""

    def estimate_lifespan(self, profile: UserProfile) -> LifespanEstimate:
        """Query Gemini to generate a lifespan estimation with automatic model fallbacks.

        Args:
            profile: User profile data.

        Returns:
            LifespanEstimate: Formatted estimation and longevity protocol.

        Raises:
            RuntimeError: If all candidate models fail to return valid predictions.
        """
        prompt = self.build_prompt(profile)
        candidate_models = [self.primary_model] + [
            m for m in self.fallback_models if m != self.primary_model
        ]

        last_error = "No models attempted"

        with httpx.Client(base_url=self.base_url, headers=self._get_headers(), timeout=35.0) as client:
            for model_name in candidate_models:
                try:
                    response = client.post(
                        "/chat/completions",
                        json={
                            "model": model_name,
                            "messages": [{"role": "user", "content": prompt}],
                            "response_format": {"type": "json_object"},
                            "temperature": 0.25,
                        },
                    )

                    if response.status_code != 200:
                        last_error = f"Model {model_name} HTTP {response.status_code}: {response.text[:120]}"
                        continue

                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = self._extract_json(content)

                    # Compute estimated death date based on birth date + lifespan years
                    birth_dt = date.fromisoformat(profile.birth_date)
                    years = float(parsed.get("estimated_lifespan_years", 80.0))
                    days_to_add = years * 365.2425
                    death_dt = datetime(birth_dt.year, birth_dt.month, birth_dt.day, 12, 0, 0, tzinfo=timezone.utc) + timedelta(days=days_to_add)

                    return LifespanEstimate(
                        estimated_lifespan_years=years,
                        estimated_death_date=death_dt.isoformat(),
                        baseline_country_expectancy=float(parsed.get("baseline_country_expectancy", 72.0)),
                        net_lifestyle_modifier_years=float(parsed.get("net_lifestyle_modifier_years", 0.0)),
                        summary=str(parsed.get("summary", "Gemini longevity analysis complete.")),
                        top_boosters=list(parsed.get("top_boosters", [])),
                        top_risks=list(parsed.get("top_risks", [])),
                        longevity_recommendations=list(parsed.get("longevity_recommendations", [])),
                    )
                except Exception as exc:
                    last_error = f"Model {model_name} invocation error: {exc}"
                    continue

        raise RuntimeError(f"Failed to generate lifespan estimation across Gemini models: {last_error}")

    def _extract_json(self, raw_text: str) -> dict[str, Any]:
        """Extract and parse JSON from model output text.

        Args:
            raw_text: Raw string response from model.

        Returns:
            dict[str, Any]: Parsed JSON dictionary.

        Raises:
            ValueError: If JSON cannot be parsed.
        """
        text = raw_text.strip()
        # Remove potential markdown code blocks
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
