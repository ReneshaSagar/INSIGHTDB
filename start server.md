# Starting the InsightDB Server

Follow these steps to get the InsightDB platform up and running on your local machine.

## 1. Prerequisites
Ensure you have Python 3.8+ installed. You will also need the service account JSON key (`insightdb-488114-05559aae354e.json`) in the project root for AI features to function.

## 2. Install Dependencies
Run the following command to install all necessary backend libraries:

```powershell
pip install flask pandas openai python-dotenv flask-cors google-auth requests
```

## 3. Launch the Backend
From the project root directory, execute the Flask entry point:

```powershell
python backend/app.py
```

## 4. Open the Dashboard
Once the terminal indicates the server is running (usually on port 5000), open your web browser and navigate to:

**[http://localhost:5000](http://localhost:5000)**

## 5. Usage
1. Use the **Upload** button on the dashboard to import your CSV datasets.
2. The system will automatically perform a **Schema Analysis** and calculate **Trust Scores**.
3. Interact with the **AI Assistant** to ask questions about your data.

---
*Created for Hackfest 2.0*
