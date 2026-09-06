from flask import Flask, jsonify
from flask_cors import CORS
import serial
import json
import joblib
import threading

app = Flask(__name__)
CORS(app)

# Load trained AI model
model = joblib.load('gridguard_model.pkl')

# Connect to ESP32 over USB Serial (Update COM port if needed)
ser = serial.Serial('COM3', 115200, timeout=1)

latest_data = {
    "temp": 0.0, "current": 0.0, "vib": 0.0, "gas": 0.0,
    "risk": 0, "status": "Normal", "unsafe": False
}

def read_esp32_loop():
    global latest_data
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("{"):
                raw = json.loads(line)
                features = [[raw['temp'], raw['current'], raw['vib'], raw['gas']]]
                
                # Get prediction probability for risk score calculation
                probabilities = model.predict_proba(features)[0]
                risk_score = round(float(max(probabilities[1:] if len(probabilities) > 1 else [0])) * 100, 1)
                
                status = "NORMAL"
                if risk_score > 70 or raw['unsafe']:
                    status = "CRITICAL FAULT"
                elif risk_score > 35:
                    status = "WARNING"

                latest_data = {
                    "temp": raw['temp'],
                    "current": raw['current'],
                    "vib": raw['vib'],
                    "gas": raw['gas'],
                    "risk": risk_score,
                    "status": status,
                    "unsafe": raw['unsafe']
                }
        except Exception:
            pass

# Start background thread to continuously read USB data
threading.Thread(target=read_esp32_loop, daemon=True).start()

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(latest_data)

@app.route('/api/simulate', methods=['POST'])
def simulate():
    ser.write(b"SIMULATE_FAULT\n")
    return jsonify({"message": "Simulation activated"})

@app.route('/api/reset', methods=['POST'])
def reset():
    ser.write(b"RESET\n")
    return jsonify({"message": "System reset"})

if __name__ == '__main__':
    app.run(port=5000, debug=False)
