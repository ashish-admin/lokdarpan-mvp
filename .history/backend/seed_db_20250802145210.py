import pandas as pd
from app import create_app, db
from app.models import Post
from app.services import analyze_emotions

app = create_app()
with app.app_context():
    print("Seeding database from mock_data.csv...")
    Post.query.delete()

    # Correct path: looks inside the /backend/data folder
    df = pd.read_csv('data/mock_data.csv')
    records = df.to_dict(orient='records')

    print("Analyzing emotions for seed data...")
    enriched_records = analyze_emotions(records)

    # Verification block to ensure analysis was successful
    if not enriched_records or 'emotion' not in enriched_records[0] or enriched_records[0]['emotion'] in ['Unknown', 'Error', None]:
        print("\n\n--- ERROR ---")
        print("Emotion analysis failed. The most likely cause is an invalid or missing GEMINI_API_KEY in your /backend/.env file.")
        raise Exception("Stopping seed due to failed emotion analysis.")

    print("Emotion analysis successful. Adding to database...")
    for record in enriched_records:
        post = Post(
            id=record.get('id'),
            timestamp=record.get('timestamp'),
            text=record.get('text'),
            latitude=record.get('latitude'),
            longitude=record.get('longitude'),
            city=record.get('city'),
            emotion=record.get('emotion')
        )
        db.session.add(post)

    db.session.commit()
    print("Database seeding complete!")