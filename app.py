import os
import socket
from flask import Flask, render_template

app = Flask(__name__)

# --- Feature flag: flip this in code for the "rebuild with new code" step ---
FEATURE_BANNER = False   # change to True in v2 to show a new feature

@app.route("/")
def index():
    return render_template(
        "index.html",
        version=os.environ.get("APP_VERSION", "v1"),
        color=os.environ.get("APP_COLOR", "#2563eb"),
        message=os.environ.get("APP_MESSAGE", "Hello from OpenShift"),
        hostname=socket.gethostname(),
        feature_banner=FEATURE_BANNER,
    )

@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
