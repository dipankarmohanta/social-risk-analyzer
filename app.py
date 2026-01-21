from flask import Flask, request, jsonify
from extractor import fetch_instagram_profile
from features import extract_features
from model import score, scale_risk

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Fake Profile Risk Analyzer</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
        body {
            padding: 30px;
            background: #f5f6fa;
        }
        .profile-img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
        }
        .card {
            border-radius: 14px;
        }
        pre {
            background: #f1f1f1;
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
        }
    </style>
</head>

<body>

<div class="container">
    <h2 class="mb-4">Instagram Fake Profile Risk Analyzer</h2>

    <!-- Search -->
    <div class="input-group mb-4">
        <input type="text" id="username" class="form-control" placeholder="Instagram username">
        <button class="btn btn-primary" onclick="analyze()">Analyze</button>
    </div>

    <!-- Current Result -->
    <div id="currentResult"></div>

    <!-- Recent Searches -->
    <h4 class="mt-5">Recent Searches</h4>
    <div class="row" id="recentSearches"></div>
</div>

<!-- Raw Data Modal -->
<div class="modal fade" id="rawDataModal" tabindex="-1">
    <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Raw Scraped Data</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <pre id="rawDataContent" style="max-height:70vh; overflow:auto;"></pre>
            </div>
        </div>
    </div>
</div>

<!-- Bootstrap JS (REQUIRED) -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

<script>
let recentProfiles = [];

function analyze() {
    const username = document.getElementById("username").value.trim();
    if (!username) {
        alert("Enter username");
        return;
    }

    fetch(`/analyze?username=${username}`)
        .then(res => res.json())
        .then(data => {
            if (data.status !== "ok") {
                alert("Profile not accessible or private");
                return;
            }

            renderCurrent(data);

            recentProfiles = recentProfiles.filter(p => p.username !== data.username);
            recentProfiles.unshift(data);
            if (recentProfiles.length > 6) recentProfiles.pop();

            renderRecent();
        });
}

function renderCurrent(data) {
    const factors = data.factors;
    let factorHtml = "";

    for (const key in factors) {
        const value = factors[key];
        const percent = Math.round(value * 100);

        let color = "bg-danger";
        let label = "High Risk";

        if (value >= 0.67) {
            color = "bg-success";
            label = "Low Risk";
        } else if (value >= 0.34) {
            color = "bg-warning";
            label = "Medium Risk";
        }

        factorHtml += `
        <div class="mb-3">
            <div class="d-flex justify-content-between">
                <strong>${key.replaceAll("_", " ")}</strong>
                <span class="badge ${color}">${label}</span>
            </div>

            <div class="progress mt-1" style="height: 10px;">
                <div class="progress-bar ${color}" style="width:${percent}%"></div>
            </div>

            <small class="text-muted">Score: ${value.toFixed(2)}</small>
        </div>`;
    }

    const html = `
    <div class="card p-4 mb-4">
        <div class="d-flex align-items-center mb-3">
            <img src="${data.profile_picture}" class="profile-img me-3">
            <div>
                <h5>${data.display_name || data.username}</h5>
                <strong>
                    Risk Rating: ${data.risk.rating} / 10
                    <span class="ms-2 badge bg-${getBandColor(data.risk.band)}">
                        ${data.risk.band} Risk
                    </span>
                </strong>
            </div>
        </div>

        ${factorHtml}

        <button class="btn btn-outline-secondary btn-sm mt-2"
                onclick='showRawData(${JSON.stringify(data.data)})'>
            View Raw Data
        </button>
    </div>`;

    document.getElementById("currentResult").innerHTML = html;
}

function renderRecent() {
    const container = document.getElementById("recentSearches");
    container.innerHTML = "";

    recentProfiles.slice(1).forEach(p => {
        container.innerHTML += `
        <div class="col-md-4 col-sm-6 mb-3">
            <div class="card p-3">
                <div class="d-flex align-items-center">
                    <img src="${p.profile_picture}" class="profile-img me-3">
                    <div>
                        <strong>${p.display_name || p.username}</strong><br>
                        <small>@${p.username}</small><br>
                        <strong>Risk: ${p.risk.rating}/10</strong>
                    </div>
                </div>
                <button class="btn btn-outline-secondary btn-sm mt-2"
                        onclick='showRawData(${JSON.stringify(p.data)})'>
                    View Raw Data
                </button>
            </div>
        </div>`;
    });
}

function getBandColor(band) {
    if (band === "Low") return "success";
    if (band === "Medium") return "warning";
    if (band === "High") return "danger";
    return "dark";
}

function showRawData(raw) {
    document.getElementById("rawDataContent").innerText =
        JSON.stringify(raw, null, 2);

    const modal = new bootstrap.Modal(
        document.getElementById("rawDataModal")
    );
    modal.show();
}
</script>

</body>
</html>

"""

@app.route("/analyze", methods=["GET"])
def analyze():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username required"})

    raw_data = fetch_instagram_profile(username)

    if raw_data["status"] == "private":
        return jsonify({
            "status": "unsupported",
            "reason": "profile_is_private",
            "data": raw_data
        })

    if raw_data["status"] != "public":
        return jsonify({
            "status": "error",
            "reason": "profile_not_accessible",
            "data": raw_data
        })

    # ✅ Correct extract_features call (positional)
    features = extract_features(
        username,
        raw_data.get("html", ""),
        profile_pic_exists=bool(raw_data.get("profile_pic"))
    )

    raw_score = score(features)
    risk = scale_risk(raw_score, features)
    raw_title = raw_data.get("display_name")
    #raw_title = raw_title.strip()

    # Remove Instagram suffix safely
    display_name = raw_title.replace(" • Instagram photos and videos", "").strip()


    return jsonify({
        "status": "ok",
        "username": username,
        # "display_name": raw_data.get("display_name"),//display_name
        "display_name": display_name,
        "profile_picture": raw_data.get("profile_pic"),
        "risk": risk,
        "factors": features,
        "data": raw_data  # Raw scraping data for audit
    })

if __name__ == "__main__":
    app.run(debug=True)
