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
    <title>Fake Profile Detection</title>

    <!-- Bootstrap CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
        body { padding: 30px; background: #f5f6fa; }
        .profile-img { width: 80px; height: 80px; border-radius: 50%; }
        .card { border-radius: 12px; }
        .high { color: red; font-weight: bold; }
        .low { color: green; font-weight: bold; }
        pre { background:#f1f1f1; padding:10px; border-radius:6px; }
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
    <div class="modal-content p-3">
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
<!-- Bootstrap JS (REQUIRED for modal) -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

<script>
function showRawData(raw) {
    const formatted = JSON.stringify(raw, null, 2);
    document.getElementById("rawDataContent").innerText = formatted;

    let modal = new bootstrap.Modal(
        document.getElementById("rawDataModal")
    );
    modal.show();
}
</script>
<script>
let recentProfiles = [];

function analyze() {
    const username = document.getElementById("username").value;
    if (!username) return alert("Enter username");

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
        const percent = value * 100;

        factorHtml += `
        <div class="mb-2">
            <input type="checkbox" checked disabled>
            <label class="ms-2">${key.replace("_", " ")}</label>
            <div class="progress mt-1" style="height: 8px;">
                <div class="progress-bar" style="width:${percent}%"></div>
            </div>
            <small>Value: ${value}</small>
        </div>`;
    }

    const card = document.createElement("div");
    card.className = "card p-4 mb-4";

    card.innerHTML = `
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
        <button class="btn btn-outline-secondary btn-sm mt-3 raw-btn" style="display:none;">
            View Raw Data
        </button>
    `;

    document.getElementById("currentResult").innerHTML = "";
    document.getElementById("currentResult").appendChild(card);

    card.querySelector(".raw-btn").addEventListener("click", () => {
        showRawData(data.data);
    });
}

function renderRecent() {
    const container = document.getElementById("recentSearches");
    container.innerHTML = "";

    recentProfiles.slice(1).forEach(p => {
        const col = document.createElement("div");
        col.className = "col-md-4 col-sm-6 mb-3";

        col.innerHTML = `
            <div class="card p-3">
                <div class="d-flex align-items-center mb-2">
                    <img src="${p.profile_picture}" class="profile-img me-3">
                    <div>
                        <strong>${p.display_name || p.username}</strong><br>
                        <strong>Risk: ${p.risk.rating}/10</strong><br>
                        <strong>@${p.username}</strong><br>
                        <span class="${p.risk.band === 'High' ? 'high' : 'low'}">
                            ${p.assessment ? p.assessment.replace('_',' ') : ''}
                        </span>
                    </div>
                </div>
                <button class="btn btn-outline-secondary btn-sm raw-btn">View Raw Data</button>
            </div>
        `;

        col.querySelector(".raw-btn").addEventListener("click", () => {
            showRawData(p.data);
        });

        container.appendChild(col);
    });
}

function getBandColor(band) {
    if (band === "Low") return "success";
    if (band === "Medium") return "warning";
    if (band === "High") return "danger";
    return "dark";
}

function showRawData(raw) {
    const formatted = JSON.stringify(raw, null, 2);
    document.getElementById("rawDataContent").innerText = formatted;

    let modal = new bootstrap.Modal(document.getElementById("rawDataModal"));
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
    raw_title = raw_title.strip()

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
