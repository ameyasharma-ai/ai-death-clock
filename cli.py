"""Interactive CLI assessment wizard for AI Death Clock.

Enables terminal users to complete life and geography questionnaire,
invoking Gemini to generate actuarial predictions and saving state.
"""

from __future__ import annotations

import sys
from gemini_engine import GeminiEngine
from models import SavedState, UserProfile, save_profile


def prompt_input(prompt: str, default: str) -> str:
    """Prompt user for input with a default value.

    Args:
        prompt: Display question string.
        default: Default value if user presses Enter.

    Returns:
        str: Selected response string.
    """
    resp = input(f"{prompt} [{default}]: ").strip()
    return resp if resp else default


def run_cli_wizard() -> SavedState:
    """Execute the interactive CLI questionnaire.

    Returns:
        SavedState: Saved application state with Gemini estimate.
    """
    print("\n" + "=" * 60)
    print("      AI DEATH CLOCK — LIFE & GEOGRAPHY ASSESSMENT      ")
    print("=" * 60)
    print("Provide details about your life to estimate your lifespan.\n")

    birth_date = prompt_input("1. Date of Birth (YYYY-MM-DD)", "1998-05-15")
    biological_sex = prompt_input("2. Biological Sex (Male/Female/Other)", "Male")
    country = prompt_input("3. Country of Residence", "India")
    city = prompt_input("4. City / Region", "Pune")
    living_area = prompt_input("5. Living Area (Urban/Suburban/Rural)", "Urban")
    air_quality = prompt_input("6. Air Quality (Clean Mountain/Moderate/High Smog)", "Moderate")
    sleep_hours = float(prompt_input("7. Daily Sleep Hours", "7.0"))
    sleep_quality = prompt_input("8. Sleep Quality (Poor/Moderate/Restorative)", "Moderate")
    exercise = prompt_input("9. Exercise Routine (Sedentary/Light/Moderate/Athletic)", "Moderate (3-4x/wk)")
    diet = prompt_input("10. Diet Pattern (Home-cooked/Mediterranean/Plant-focused/Fast-food)", "Balanced Home-cooked")
    smoking = prompt_input("11. Smoking Status (Non-smoker/Former/Vaper/Smoker)", "Non-smoker")
    alcohol = int(prompt_input("12. Alcohol drinks per week", "1"))
    caffeine = int(prompt_input("13. Caffeine cups per day", "2"))
    stress = int(prompt_input("14. Daily Stress Level (1-10)", "5"))
    work = prompt_input("15. Work Type (Desk/Active/Physical)", "Desk / Sedentary")
    social = prompt_input("16. Social Tribe (Strong/Moderate/Isolated)", "Strong Family & Friends")
    purpose = prompt_input("17. Sense of Life Purpose / Ikigai (High/Moderate/Searching)", "High / Clear Mission")
    family = prompt_input("18. Family Longevity History (Exceptional 85+/Average 75/Below 70)", "Exceptional (85+)")
    conditions = prompt_input("19. Chronic Health Conditions", "None")
    fasting = prompt_input("20. Fasting Protocol (e.g. 16:8, None)", "16:8 intermittent fasting")
    supplements = prompt_input("21. Supplements / Longevity Stack", "Creatine 5g, Vitamin D3+K2, Omega-3")
    notes = prompt_input("22. Additional Personal Notes / Unique Details", "None provided")

    custom_fields = {}
    if fasting and fasting != "None":
        custom_fields["Fasting Protocol"] = fasting
    if supplements and supplements != "None":
        custom_fields["Supplements & Longevity Stack"] = supplements

    profile = UserProfile(
        birth_date=birth_date,
        biological_sex=biological_sex,
        country=country,
        city=city,
        living_area=living_area,
        air_quality=air_quality,
        sleep_hours=sleep_hours,
        sleep_quality=sleep_quality,
        exercise_frequency=exercise,
        diet_type=diet,
        smoking_status=smoking,
        alcohol_units_per_week=alcohol,
        caffeine_daily_cups=caffeine,
        stress_level=stress,
        work_nature=work,
        social_connection=social,
        sense_of_purpose=purpose,
        family_longevity=family,
        chronic_conditions=conditions,
        personal_notes=notes if notes != "None provided" else "",
        custom_fields=custom_fields,
    )

    print("\n⏳ Consulting Google Gemini Longevity Engine...")
    engine = GeminiEngine()
    try:
        estimate = engine.estimate_lifespan(profile)
    except Exception as exc:
        print(f"\n❌ Error contacting Gemini: {exc}")
        sys.exit(1)

    state = SavedState(profile=profile, estimate=estimate)
    save_profile(state)

    print("\n" + "=" * 60)
    print("                ACTUARIAL RESULTS SUMMARY               ")
    print("=" * 60)
    print(f"• Estimated Lifespan:           {estimate.estimated_lifespan_years:.1f} years")
    print(f"• Baseline National Expectancy: {estimate.baseline_country_expectancy:.1f} years")
    print(f"• Net Lifestyle Modifier:       {estimate.net_lifestyle_modifier_years:+.1f} years")
    print(f"• Estimated End-of-Life Date:   {estimate.estimated_death_date}")
    print(f"\nSummary:\n{estimate.summary}\n")

    if estimate.top_boosters:
        print("✦ Longevity Boosters:")
        for b in estimate.top_boosters:
            print(f"   + {b}")

    if estimate.top_risks:
        print("\n⚠ Longevity Risks:")
        for r in estimate.top_risks:
            print(f"   - {r}")

    if estimate.longevity_recommendations:
        print("\n⚡ Lifespan Expansion Protocol:")
        for rec in estimate.longevity_recommendations:
            print(f"   ➜ {rec}")

    print("\n✓ Profile saved to disk. Ready to display desktop widget!\n")
    return state


if __name__ == "__main__":
    run_cli_wizard()
