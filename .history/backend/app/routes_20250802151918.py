from flask import Blueprint, jsonify, request, current_app
from .models import Post, User
from . import db
from flask_login import login_user, logout_user, current_user
import os
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import json
from .services import analyze_emotions 

bp = Blueprint('main', __name__)

wards_gdf = None
def load_wards_geojson():
    global wards_gdf
    if wards_gdf is None:
        # --- THIS IS THE ROBUST AND CORRECTED FILE PATH ---
        # It builds an absolute path from the /backend folder root.
        geojson_path = os.path.join(current_app.root_path, 'data', 'ghmc_wards.geojson')
        
        if not os.path.exists(geojson_path):
            raise FileNotFoundError(f"GeoJSON file not found at path: {geojson_path}")
            
        wards_gdf = gpd.read_file(geojson_path)
    return wards_gdf

# --- Authentication and other routes ---
@bp.route('/api/v1/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user is None or not user.check_password(data.get('password')):
        return jsonify({'message': 'Invalid username or password'}), 401
    login_user(user)
    return jsonify({'message': 'Logged in successfully'}), 200

@bp.route('/api/v1/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/api/v1/status', methods=['GET'])
def status():
    if current_user.is_authenticated:
        return jsonify({'logged_in': True})
    else:
        return jsonify({'logged_in': False})

# --- Protected API Endpoints ---
@bp.route('/api/v1/analytics', methods=['GET'])
def analytics():
    if not current_user.is_authenticated:
        return jsonify({'message': 'Authentication required'}), 401
    posts = Post.query.all()
    return jsonify([post.to_dict() for post in posts])

# --- Granular Analytics Endpoint ---
@bp.route('/api/v1/analytics/granular', methods=['GET'])
def granular_analytics():
    if not current_user.is_authenticated:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        wards = load_wards_geojson()
        posts = Post.query.filter(Post.latitude.isnot(None), Post.longitude.isnot(None)).all()
        if not posts: return jsonify([])

        posts_df = pd.DataFrame([p.to_dict() for p in posts])
        posts_df['longitude'] = pd.to_numeric(posts_df['longitude'])
        posts_df['latitude'] = pd.to_numeric(posts_df['latitude'])
        geometry = [Point(xy) for xy in zip(posts_df['longitude'], posts_df['latitude'])]
        posts_gdf = gpd.GeoDataFrame(posts_df, geometry=geometry, crs="EPSG:4326")
        
        if wards.crs is None: wards.set_crs("EPSG:4326", inplace=True)
        if posts_gdf.crs != wards.crs: posts_gdf.to_crs(wards.crs, inplace=True)

        joined_gdf = gpd.sjoin(posts_gdf, wards, how="inner", predicate='within')

        if joined_gdf.empty: return jsonify([])
            
        emotion_counts = joined_gdf.groupby(['name', 'emotion']).size().unstack(fill_value=0)
        dominant_emotion = emotion_counts.idxmax(axis=1)
        
        results = []
        for ward_name, emotion in dominant_emotion.items():
            ward_data = wards[wards['name'] == ward_name]
            results.append({
                'ward_name': ward_name,
                'dominant_emotion': emotion,
                'post_count': int(emotion_counts.loc[ward_name].sum()),
                'geometry': ward_data.geometry.__geo_interface__['features'][0]['geometry']
            })
        return jsonify(results)
    except Exception as e:
        print(f"Error in granular analytics: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An error occurred during geo-analysis"}), 500

# --- Strategic Summary Endpoint ---
@bp.route('/api/v1/strategic-summary', methods=['GET'])
def strategic_summary():
    if not current_user.is_authenticated:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        posts = Post.query.all()
        if not posts:
            return jsonify({"summary": "Not enough data for analysis."})

        df = pd.DataFrame([p.to_dict() for p in posts])
        emotion_counts = df['emotion'].value_counts()
        
        positive_emotions = ['Hope', 'Joy']
        negative_emotions = ['Anger', 'Anxiety', 'Sadness', 'Disgust']

        positive_counts = emotion_counts[emotion_counts.index.isin(positive_emotions)]
        negative_counts = emotion_counts[emotion_counts.index.isin(negative_emotions)]

        if positive_counts.empty or negative_counts.empty:
             return jsonify({"summary": "Not enough diverse emotional data for a strategic summary."})

        top_positive = positive_counts.idxmax()
        top_negative = negative_counts.idxmax()

        positive_context = df[df['emotion'] == top_positive]['text'].iloc[0]
        negative_context = df[df['emotion'] == top_negative]['text'].iloc[0]

        prompt = f"""
        As a political strategist, analyze the following sentiment data.
        Provide a brief, actionable strategic summary with two parts: "Opportunity" and "Threat".

        - The primary positive emotion is "{top_positive}". A key topic driving this is "{positive_context}".
        - The primary negative emotion is "{top_negative}". A key topic driving this is "{negative_context}".

        Based on this, what is the single biggest opportunity to amplify, and what is the single biggest threat to mitigate?
        Return your response as a valid JSON object with two keys: "opportunity" and "threat".
        """

        summary_json = analyze_emotions_for_summary(prompt)
        return jsonify(summary_json)

    except Exception as e:
        print(f"Error in strategic summary: {e}")
        return jsonify({"error": "Failed to generate strategic summary."}), 500

def analyze_emotions_for_summary(prompt):
    import google.generativeai as genai
    model = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        generation_config={"response_mime_type": "application/json"}
    )
    response = model.generate_content(prompt)
    return json.loads(response.text)