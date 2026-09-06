import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Load collected dataset
df = pd.read_csv('sensor_data.csv')

X = df[['temp', 'current', 'vib', 'gas']]
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model performance
predictions = model.predict(X_test)
print("=== Model Evaluation ===")
print(classification_report(y_test, predictions))

# Save model file
joblib.dump(model, 'gridguard_model.pkl')
print("Model saved successfully as 'gridguard_model.pkl'")
