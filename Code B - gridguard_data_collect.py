import serial
import json
import csv
import time

# Change 'COM3' to the actual USB port of your ESP32
ser = serial.Serial('COM3', 115200, timeout=1)
time.sleep(2)

print("--- GRIDGUARD AI DATA COLLECTION ---")
label = input("Enter label for this session (0 = Normal, 1 = Overload, 2 = Anomaly): ")

with open('sensor_data.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    # Write header if file is empty
    if file.tell() == 0:
        writer.writerow(['temp', 'current', 'vib', 'gas', 'label'])
    
    print("Collecting data... Press Ctrl+C to stop.")
    try:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("{"):
                data = json.loads(line)
                writer.writerow([data['temp'], data['current'], data['vib'], data['gas'], label])
                print(f"Recorded: {data} -> Label: {label}")
    except KeyboardInterrupt:
        print("\nData collection stopped.")
