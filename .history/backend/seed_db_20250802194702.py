# backend/seed_db.py

import pandas as pd
import time
import json
from app import create_app, db
from app.models import Post, User
from app.services import analyze_emotions_and_drivers
from werkzeug.security import generate_password_hash

def seed_database():
    """
    Seeds the database from mock_data.csv.
    - Clears existing data.
    - Creates a default user.
    - Reads mock data, analyzes it for emotions and drivers, and populates the posts table.
    """
    app = create_app()
    with app.app_context():
        print("Dropping all tables and recreating...")
        db.drop_all()
        db.create_all()

        print("Creating default user 'admin' with password 'password'...")
        default_user = User(username='admin')
        default_user.set_password('password')
        db.session.add(default_user)
        db.session.commit()
        print("Default user created.")

        try:
            df = pd.read_csv('mock_data.csv')
            # Prepare records for the AI service, ensuring each has a unique ID for mapping
            records_to_analyze = [
                {'id': index + 1, 'text': row['text']}
                for index, row in df.iterrows()
            ]
        except FileNotFoundError:
            print("Error: mock_data.csv not found in the project root directory. Aborting.")
            return

        print(f"Found {len(records_to_analyze)} records. Analyzing with Gemini AI...")
        
        # Call the batch analysis function from your services
        analyzed_records = analyze_emotions_and_drivers(records_to_analyze)

        # Create a dictionary for easy lookup of analysis results by id
        analysis_map = {item['id']: item for item in analyzed_records}

        print("Populating database with posts...")
        for index, row in df.iterrows():
            record_id = index + 1
            analysis_result = analysis_map.get(record_id, {'emotion': 'Error', 'drivers': []})
            
            new_post = Post(
                text=row['text'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                city=row['city'],
                timestamp=row.get('timestamp', 'N/A'),
                emotion=analysis_result['emotion'],
                drivers=analysis_result.get('drivers', []) # Ensure drivers is always a list
            )
            db.session.add(new_post)

        print("Committing all new posts to the database...")
        db.session.commit()
        print("Database seeding complete!")

if __name__ == '__main__':
    seed_database()