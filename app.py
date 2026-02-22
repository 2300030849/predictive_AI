from flask import Flask, render_template, request, jsonify, send_file
import joblib
import pandas as pd
import random
import sqlite3
from io import BytesIO
from config import MODEL_PATH, ALERT_THRESHOLD
from utils import init_db, log_prediction, fetch_logs

# PDF & Graph
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Image
import matplotlib.pyplot as plt

app = Flask(__name__)
model = joblib.load(MODEL_PATH)
init_db()

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- AUTO MODE ----------------
@app.route("/auto_predict/<machine_id>")
def auto_predict(machine_id):

    air_temp = round(random.uniform(295, 320), 2)
    process_temp = round(random.uniform(305, 340), 2)
    rot_speed = round(random.uniform(1200, 1800), 2)
    torque = round(random.uniform(30, 60), 2)
    tool_wear = round(random.uniform(0, 200), 2)

    features = pd.DataFrame([{
        "air_temp": air_temp,
        "process_temp": process_temp,
        "rot_speed": rot_speed,
        "torque": torque,
        "tool_wear": tool_wear
    }])

    prediction = model.predict(features)[0]
    probability = round(model.predict_proba(features)[0][1] * 100, 2)

    status = "FAILURE RISK" if prediction == 1 else "HEALTHY"

    log_prediction(machine_id, air_temp, process_temp,
                   rot_speed, torque, tool_wear,
                   probability, status)

    return jsonify({
        "probability": probability,
        "status": status,
        "air_temp": air_temp,
        "process_temp": process_temp,
        "rot_speed": rot_speed,
        "torque": torque,
        "tool_wear": tool_wear
    })

# ---------------- MANUAL MODE ----------------
@app.route("/manual_predict", methods=["POST"])
def manual_predict():

    machine_id = request.form["machine_id"]

    air_temp = float(request.form["air_temp"])
    process_temp = float(request.form["process_temp"])
    rot_speed = float(request.form["rot_speed"])
    torque = float(request.form["torque"])
    tool_wear = float(request.form["tool_wear"])

    features = pd.DataFrame([{
        "air_temp": air_temp,
        "process_temp": process_temp,
        "rot_speed": rot_speed,
        "torque": torque,
        "tool_wear": tool_wear
    }])

    prediction = model.predict(features)[0]
    probability = round(model.predict_proba(features)[0][1] * 100, 2)
    status = "FAILURE RISK" if prediction == 1 else "HEALTHY"

    return jsonify({
        "probability": probability,
        "status": status
    })

# ---------------- PDF REPORT ----------------
@app.route("/download_report")
def download_report():

    logs = fetch_logs()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Factory Predictive Maintenance Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    data = [["Machine", "Probability", "Status"]]

    probabilities = []

    for row in logs[-10:]:
        data.append([row[1], row[7], row[8]])
        probabilities.append(row[7])

    table = Table(data)
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Generate Graph
    plt.figure()
    plt.plot(probabilities)
    plt.title("Recent Failure Probability Trend")
    plt.xlabel("Recent Records")
    plt.ylabel("Probability (%)")
    plt.savefig("temp_graph.png")
    plt.close()

    elements.append(Image("temp_graph.png", width=400, height=200))

    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name="Factory_Report.pdf",
                     mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)