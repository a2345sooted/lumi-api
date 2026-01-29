from langchain_core.tools import tool
from typing import Dict, Any

@tool
def get_hydration_rubric() -> Dict[str, Any]:
    """
    Returns the evidence-based hydration estimation model (rubric) used to determine 
    a user's daily water intake goals based on various factors.
    Use this tool when the user asks how much water they should drink, or when you need 
    to calculate a hydration goal.
    """
    return {
        "baseline_requirements": {
            "weight_based": "0.5 - 0.6 oz per pound of body weight per day",
            "adequate_intake_ai_guidelines": {
                "men": {"total_water": "125 oz/day", "fluids_target": "~100 oz/day"},
                "women": {"total_water": "91 oz/day", "fluids_target": "~75 oz/day"},
                "note": "AI includes ~20% water from food"
            }
        },
        "adjustments": {
            "body_size_and_composition": {
                "very_large_or_muscular": "+10-20%",
                "small_body_size": "-10%"
            },
            "climate_and_temperature": {
                "warm": "+16-20 oz/day",
                "hot_humid": "+32-50 oz/day",
                "cold_dry": "+8-14 oz/day"
            },
            "activity_level": {
                "light_exercise": "+10-16 oz/hour",
                "moderate_exercise": "+16-24 oz/hour",
                "heavy_sweating": "+32 oz/hour"
            },
            "dietary_factors": {
                "high_protein": "+10-16 oz/day",
                "high_fiber": "+8-14 oz/day",
                "high_sodium": "Increase water needs"
            },
            "substances": {
                "heavy_caffeine_use": "+8-14 oz/day",
                "alcohol": "+10-24 oz/day (depending on amount)"
            },
            "physiological_states": {
                "pregnancy": "+10 oz/day",
                "breastfeeding": "+24-34 oz/day",
                "fever_vomiting_diarrhea": "+32-68 oz/day (or medical attention)"
            },
            "other_factors": {
                "altitude": "Increase water loss via respiration",
                "respiratory_rate_cpap": "Increase water loss",
                "age_related": "Older adults may need reminders due to thirst decline",
                "dry_environment_work": "Increase needs"
            }
        },
        "medical_guardrails": {
            "fluid_restriction_required": [
                "Heart failure",
                "Advanced kidney disease",
                "SIADH",
                "Dialysis"
            ],
            "higher_intake_recommended": [
                "Kidney stones",
                "Frequent UTIs",
                "Diabetes (if uncontrolled)"
            ],
            "safety_message": "Do not increase fluid without clinician guidance if you have conditions requiring fluid restriction."
        },
        "monitoring_guidance": {
            "indicators_of_good_hydration": [
                "Pale yellow urine",
                "Minimal thirst",
                "Stable weight",
                "No dizziness"
            ]
        }
    }
