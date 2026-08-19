import re


# Canonical skill name -> possible ways it can appear in a resume
SKILL_ALIASES = {
    "Python": ["python"],
    "Java": ["java"],
    "C": ["c"],
    "C++": ["c++", "cpp"],
    "SQL": ["sql"],
    "JavaScript": ["javascript", "js"],
    "HTML": ["html"],
    "CSS": ["css"],
    "React": ["react", "react.js"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Express": ["express", "express.js"],
    "MongoDB": ["mongodb", "mongo db"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "Django": ["django"],

    "Machine Learning": [
        "machine learning",
        "machine-learning"
    ],
    "Deep Learning": [
        "deep learning",
        "deep-learning"
    ],
    "Artificial Intelligence": [
        "artificial intelligence",
        "artificial intelligence"
    ],
    "Computer Vision": [
        "computer vision"
    ],
    "NLP": [
        "nlp",
        "natural language processing"
    ],

    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Keras": ["keras"],
    "Scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn"
    ],
    "XGBoost": ["xgboost"],
    "OpenCV": ["opencv", "open cv"],
    "YOLO": ["yolo"],
    "NumPy": ["numpy"],
    "Pandas": ["pandas"],

    "Git": ["git"],
    "GitHub": ["github"],
    "Linux": ["linux"],
    "Docker": ["docker"],
    "AWS": ["aws", "amazon web services"],

    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Excel": ["excel"],

    "Arduino": ["arduino"],
    "ESP32": ["esp32"],
    "Raspberry Pi": ["raspberry pi"],
    "IoT": [
        "iot",
        "internet of things"
    ],
    "Embedded Systems": [
        "embedded systems",
        "embedded system"
    ],
    "Robotics": ["robotics"],
    "ROS": ["ros"],
    "Drone Technology": [
        "drone technology",
        "drones"
    ],

    "MERN": ["mern"],
    "REST APIs": [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis"
    ],

    "Data Analysis": ["data analysis"],
    "Data Preprocessing": ["data preprocessing"],
    "Statistics": [
        "statistics",
        "statistical analysis"
    ],
}


def contains_skill(text: str, alias: str) -> bool:
    """
    Check for a skill without accidentally matching
    parts of larger words.
    """

    pattern = r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)"

    return re.search(
        pattern,
        text.lower()
    ) is not None


def extract_skills(text: str) -> list[str]:
    """
    Extract known skills from resume text.

    Returns canonical skill names with duplicates removed.
    """

    if not text:
        return []

    found_skills = []

    for canonical_name, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            if contains_skill(text, alias):
                found_skills.append(canonical_name)
                break

    return sorted(found_skills)