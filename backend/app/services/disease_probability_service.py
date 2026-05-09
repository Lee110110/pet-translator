import json
import pathlib
from datetime import date


def _load_disease_knowledge() -> list[dict]:
    path = pathlib.Path(__file__).parent.parent / "knowledge" / "cat_diseases.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_breed_knowledge() -> list[dict]:
    path = pathlib.Path(__file__).parent.parent / "knowledge" / "breed_info.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_disease_probabilities(
    breed: str | None,
    birthday: date | None,
    symptoms: list[str],
) -> list[dict]:
    """Calculate disease probability ranking based on breed, age, and symptoms.

    Returns list of dicts with: disease, probability_range, matching_symptoms,
    common_breeds, risk_age, required_tests, urgency
    """
    diseases = _load_disease_knowledge()
    breeds = _load_breed_knowledge()

    age_text = ""
    if birthday:
        age_days = (date.today() - birthday).days
        if age_days < 365:
            age_text = f"{age_days // 30}个月"
        else:
            age_text = f"{age_days // 365}岁"

    # Find breed-specific disease names
    breed_disease_names = set()
    if breed:
        for b in breeds:
            if breed in b["breed"] or b["breed"].startswith(breed):
                breed_disease_names = set(b["common_diseases"])
                break

    results = []
    for disease in diseases:
        # Symptom overlap score
        disease_symptoms = disease.get("key_symptoms", [])
        matching = [s for s in disease_symptoms if any(symptom.lower() in s.lower() or s.lower() in symptom.lower() for symptom in symptoms)]
        overlap_ratio = len(matching) / max(len(disease_symptoms), 1) if disease_symptoms else 0

        # Breed relevance
        common_breeds = disease.get("common_breeds", [])
        breed_match = False
        if breed:
            breed_match = any(breed in cb or cb in breed or cb == "所有品种" for cb in common_breeds)

        # Age relevance
        risk_age = disease.get("risk_age", "")
        age_match = False
        if age_text and risk_age:
            if "以上" in risk_age:
                threshold = risk_age.replace("以上高发", "").replace("以上", "").strip()
                try:
                    if "岁" in threshold:
                        age_match = int(age_text.replace("岁", "")) >= int(threshold.replace("岁", ""))
                    elif "月" in threshold:
                        age_match = int(age_text.replace("个月", "")) >= int(threshold.replace("月", ""))
                except ValueError:
                    age_match = True  # Can't parse, assume relevant
            elif "任何年龄" in risk_age:
                age_match = True

        # Combined score
        score = overlap_ratio * 0.5
        if breed_match:
            score += 0.25
        if breed_disease_names and disease["disease"] in breed_disease_names:
            score += 0.15
        if age_match:
            score += 0.1

        # Probability range
        if score >= 0.7:
            probability_range = "高概率(60-90%)"
        elif score >= 0.4:
            probability_range = "中概率(30-60%)"
        elif score >= 0.2:
            probability_range = "低概率(10-30%)"
        elif score > 0:
            probability_range = "极低概率(<10%)"
        else:
            continue  # Skip diseases with zero relevance

        results.append({
            "disease": disease["disease"],
            "probability_range": probability_range,
            "matching_symptoms": matching,
            "common_breeds": common_breeds,
            "risk_age": risk_age,
            "required_tests": disease.get("required_tests", []),
            "urgency": disease.get("urgency", ""),
        })

    # Sort by score (desc) - we compute score inline
    results.sort(key=lambda r: _score_from_range(r["probability_range"]), reverse=True)
    return results[:5]


def _score_from_range(probability_range: str) -> float:
    if "高概率" in probability_range:
        return 0.7
    if "中概率" in probability_range:
        return 0.4
    if "低概率" in probability_range:
        return 0.2
    return 0.05