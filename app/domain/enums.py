from enum import Enum as PyEnum

class ActivityType(str, PyEnum):
    RUNNING = "running"
    WALKING = "walking"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    WEIGHT_TRAINING = "weight_training"
    CIRCUIT_TRAINING = "circuit_training"
    YOGA = "yoga"
    PILATES = "pilates"
    HIKING = "hiking"
    DANCING = "dancing"
    MARTIAL_ARTS = "martial_arts"
    BOXING = "boxing"
    CROSSFIT = "crossfit"
    ELLIPTICAL = "elliptical"
    ROWING = "rowing"
    STAIR_CLIMBER = "stair_climber"
    JUMP_ROPE = "jump_rope"
    FUNCTIONAL_STRENGTH = "functional_strength"
    OTHER = "other"

class HealthMetricType(str, PyEnum):
    """Types of health metrics that can be tracked."""
    # Vital Signs
    HEART_RATE = "heart_rate"  # BPM
    BLOOD_PRESSURE = "blood_pressure"
    BLOOD_OXYGEN = "blood_oxygen"  # SpO2 %
    BODY_TEMPERATURE = "body_temperature"  # °C
    RESPIRATORY_RATE = "respiratory_rate"  # breaths per minute

    # Body Composition
    BODY_WEIGHT = "body_weight"
    BODY_HEIGHT = "height"  # cm
    BMI = "bmi"  # kg/m²
    BODY_FAT_PERCENTAGE = "body_fat_percentage"  # %
    MUSCLE_MASS = "muscle_mass"  # kg
    BONE_MASS = "bone_mass"  # kg
    WATER_PERCENTAGE = "water_percentage"  # %

    # Blood Tests
    BLOOD_GLUCOSE = "blood_glucose"
    FASTING_GLUCOSE = "fasting_glucose"  # mg/dL
    HBA1C = "hba1c"  # %
    CHOLESTEROL = "cholesterol"
    HDL_CHOLESTEROL = "hdl_cholesterol"  # mg/dL
    LDL_CHOLESTEROL = "ldl_cholesterol"  # mg/dL
    TRIGLYCERIDES = "triglycerides"  # mg/dL

    # Activity and Fitness
    STEPS = "steps"  # count
    ACTIVE_MINUTES = "active_minutes"  # minutes
    EXERCISE_MINUTES = "exercise_minutes"  # minutes
    CALORIES_BURNED = "calories_burned"  # kcal
    RESTING_HEART_RATE = "resting_heart_rate"  # BPM
    VO2_MAX = "vo2_max"  # mL/kg/min

    # Sleep
    SLEEP_QUALITY = "sleep_quality"
    SLEEP_DURATION = "sleep_duration"  # minutes
    SLEEP_EFFICIENCY = "sleep_efficiency"  # %
    DEEP_SLEEP_DURATION = "deep_sleep_duration"  # minutes
    REM_SLEEP_DURATION = "rem_sleep_duration"  # minutes
    SLEEP_SCORE = "sleep_score"  # 0-100

    # Nutrition
    CALORIES_CONSUMED = "calories_consumed"  # kcal
    PROTEIN_INTAKE = "protein_intake"  # g
    CARBS_INTAKE = "carbs_intake"  # g
    FAT_INTAKE = "fat_intake"  # g
    FIBER_INTAKE = "fiber_intake"  # g
    SUGAR_INTAKE = "sugar_intake"  # g
    WATER_INTAKE = "water_intake"  # mL

    # Mental Wellbeing
    STRESS_LEVEL = "stress_level"  # 1-10
    MOOD = "mood"
    MOOD_LEVEL = "mood_level"  # 1-10
    ENERGY_LEVEL = "energy_level"  # 1-10
    PAIN_LEVEL = "pain_level" # 1-10