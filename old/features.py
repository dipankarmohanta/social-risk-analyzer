import math

def username_entropy(username):
    probs = [username.count(c) / len(username) for c in set(username)]
    return -sum(p * math.log2(p) for p in probs)

def extract_features(username, html_text, profile_pic_exists):
    # 1. Username entropy
    entropy = username_entropy(username) / 5.0
    entropy = min(entropy, 1.0)

    # 2. Public footprint
    footprint = min(html_text.lower().count("post") / 20.0, 1.0)

    # 3. Profile completeness (username length heuristic)
    completeness = 1.0 if len(username) > 5 else 0.3

    # 4. Profile image existence
    image_score = 1.0 if profile_pic_exists else 0.0

    # 5. Account age (estimated)
    if footprint > 0.6 and profile_pic_exists:
        age_score = 0.8
    elif footprint > 0.3:
        age_score = 0.5
    else:
        age_score = 0.2

    return {
        "username_entropy": round(entropy, 2),
        "public_footprint": round(footprint, 2),
        "profile_completeness": round(completeness, 2),
        "profile_image_presence": image_score,
        "account_age_estimated": age_score
    }
