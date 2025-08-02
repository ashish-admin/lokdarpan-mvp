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
        # --- THIS IS THE NEW, SIMPLER FILE PATH ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        geojson_path = os.path.join(current_dir, 'data', 'ghmc_wards.geojson')
        
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

# (Keep all other routes and imports the same)

# --- NEW, UPGRADED STRATEGIC SUMMARY ENDPOINT ---
@bp.route('/api/v1/strategic-summary', methods=['GET'])
def strategic_summary():
    if not current_user.is_authenticated:
        return jsonify({'message': 'Authentication required'}), 401

    try:
        posts = Post.query.all()
        if not posts or len(posts) < 10: # Require a minimum amount of data
            return jsonify({"error": "Not enough data for a reliable analysis."})

        df = pd.DataFrame([p.to_dict() for p in posts])
        emotion_counts = df['emotion'].value_counts()

        positive_emotions = ['Hope', 'Joy']
        negative_emotions = ['Anger', 'Anxiety', 'Sadness', 'Disgust']

        positive_counts = emotion_counts[emotion_counts.index.isin(positive_emotions)]
        negative_counts = emotion_counts[emotion_counts.index.isin(negative_emotions)]

        if positive_counts.empty or negative_counts.empty:
            return jsonify({"error": "Not enough diverse emotional data for a strategic summary."})

        top_positive_emotion = positive_counts.idxmax()
        top_negative_emotion = negative_counts.idxmax()

        # Find the most common negative topic by looking at the most frequent angry/anxious post
        top_negative_post = df[df['emotion'] == top_negative_emotion]['text'].mode()[0]
        top_positive_post = df[df['emotion'] == top_positive_emotion]['text'].mode()[0]

        # This is the new, more sophisticated prompt
        prompt = f"""
        You are an expert political strategist for a campaign in Hyderabad, India. Your goal is to provide a clear, actionable intelligence briefing based on public sentiment data.

        **Analysis of Raw Intelligence:**
        - The dominant positive emotion detected is "{top_positive_emotion}", strongly associated with topics like "{top_positive_post}".
        - The dominant negative emotion detected is "{top_negative_emotion}", strongly associated with topics like "{top_negative_post}".

        **Your Task:**
        Generate a strategic response in JSON format. The JSON object must contain the following keys:
        1.  "analysis": A brief, one-sentence analysis of the current political landscape based on the emotions.
        2.  "opportunity": A specific, actionable strategy to amplify the positive sentiment.
        3.  "threat": A specific, actionable strategy to mitigate or counter the negative sentiment.
        4.  "suggested_post": A sample social media post (in English) that directly executes the "threat" mitigation strategy. This post must be empathetic, address the core issue, and pivot to a positive message.

        Provide only the raw JSON object as your response.
        """

        summary_json = generate_ai_response(prompt)
        return jsonify(summary_json)

    except Exception as e:
        print(f"Error in strategic summary: {e}")
        return jsonify({"error": "Failed to generate strategic summary."}), 500

def generate_ai_response(prompt):
    # Helper function to call the Gemini API
    import google.generativeai as genai
    model = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        generation_config={"response_mime_type": "application/json"}
    )
    response = model.generate_content(prompt)
    return json.loads(response.text)