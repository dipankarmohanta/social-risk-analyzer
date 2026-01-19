import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

MODEL_PATH = "risk_model.joblib"

FEATURE_ORDER = [
    "username_entropy",
    "public_footprint",
    "profile_completeness",
    "profile_image_presence",
    "account_age_estimated"
]

def train_model():
    # Synthetic training data (normal vs suspicious behavior)
    X = np.array([
        [0.2, 0.8, 1.0, 1.0, 0.9],  # normal
        [0.3, 0.7, 1.0, 1.0, 0.8],
        [0.6, 0.2, 0.3, 0.0, 0.2],  # suspicious
        [0.7, 0.1, 0.3, 0.0, 0.1],
        [0.4, 0.6, 0.8, 1.0, 0.7],
        [0.8, 0.1, 0.2, 0.0, 0.1]
    ])

    model = IsolationForest(
        n_estimators=100,
        contamination=0.3,
        random_state=42
    )

    model.fit(X)
    joblib.dump(model, MODEL_PATH)
    return model


def load_model():
    if not os.path.exists(MODEL_PATH):
        return train_model()
    return joblib.load(MODEL_PATH)


model = load_model()


def score(features: dict):
    x = np.array([[features[f] for f in FEATURE_ORDER]])
    anomaly_score = model.decision_function(x)[0]

    # Convert to risk signal (higher = more risky)
    risk_signal = max(0.0, -anomaly_score)

    return risk_signal
def scale_risk(raw_score, features=None):
    """
    Convert risk signal into meaningful human risk
    """

    # Base risk so score is never zero
    base_risk = 15  

    # ML contribution
    ml_risk = min(raw_score * 60, 60)

    # Rule-based penalties (this is how real systems work)
    rule_risk = 0

    if features:
        if features["profile_image_presence"] == 0:
            rule_risk += 15
        if features["account_age_estimated"] < 0.3:
            rule_risk += 10
        if features["public_footprint"] == 0:
            rule_risk += 10
        if features["username_entropy"] > 0.75:
            rule_risk += 10

    score_100 = min(100, int(base_risk + ml_risk + rule_risk))
    rating_10 = round(score_100 / 10, 1)

    if score_100 < 35:
        band = "Low"
    elif score_100 < 70:
        band = "Medium"
    else:
        band = "High"

    return {
        "score": score_100,
        "rating": rating_10,
        "band": band
    }


