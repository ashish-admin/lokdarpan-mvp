# backend/app/services.py

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables and configure the API key
load_dotenv()
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')

if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please ensure it is set in your /backend/.env file.")
genai.configure(api_key=GOOGLE_API_KEY)


def analyze_emotions_and_drivers(records):
    """
    Analyzes a list of records for a sophisticated range of emotions AND their root cause drivers
    using Gemini in JSON Mode. This is the upgraded function.
    """
    model = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        generation_config={"response_mime_type": "application/json"}
    )

    # --- THIS IS THE UPGRADED PROMPT ---
    prompt = f"""
    You are a sophisticated political analyst. For each text entry in the following list, perform two tasks:
    1.  Analyze the dominant emotion. Classify it into one of these exact categories: [Hope, Anger, Joy, Anxiety, Sadness, Disgust, Apathy].
    2.  Identify the root cause. Extract a list of 1 to 3 specific keywords, topics, or proper nouns that are the primary drivers of that emotion.

    Return your response as a single, valid JSON object with a single key "analysis" which contains an array. Each object in the array must have an "id", its analyzed "emotion", and a "drivers" list.

    Input Data:
    {json.dumps(records)}

    Example Output Format:
    {{
        "analysis": [
            {{
                "id": 1,
                "emotion": "Anger",
                "drivers": ["road conditions", "potholes"]
            }},
            {{
                "id": 2,
                "emotion": "Hope",
                "drivers": ["new metro line", "development"]
            }}
        ]
    }}
    """
    # ------------------------------------
    
    try:
        response = model.generate_content(prompt)
        response_data = json.loads(response.text)
        
        # NEW: The key is now "analysis" to reflect the richer data
        analysis_data = response_data['analysis']

        # Create a map for quick lookups
        analysis_map = {int(item['id']): {'emotion': item['emotion'], 'drivers': item.get('drivers', [])} for item in analysis_data}

        # Enrich the original records with both emotion and drivers
        for record in records:
            record_id = record.get('id')
            if record_id in analysis_map:
                record['emotion'] = analysis_map[record_id]['emotion']
                record['drivers'] = analysis_map[record_id]['drivers']
            else:
                record['emotion'] = 'Unknown'
                record['drivers'] = []
        
        return records

    except Exception as e:
        print(f"An error occurred during AI analysis: {e}")
        if 'response' in locals():
            print("--- Full AI Response Text ---")
            print(response.text)
            print("-----------------------------")
        
        # Ensure records are returned with default values on error
        for record in records:
            record['emotion'] = 'Error'
            record['drivers'] = []
        return records