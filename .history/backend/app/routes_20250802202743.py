from flask import Blueprint, jsonify, request, current_app
from .models import Post, User
from . import db
from flask_login import login_user, logout_user, current_user, login_required
import os
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import json
from collections import Counter
import google.generativeai as genai
from sqlalchemy import distinct # <-- Crucial import for the new wards route

bp = Blueprint('api', __name__, url_prefix='/api/v1')

# --- Helper function for GeoJSON loading ---
wards_gdf = None
def load_wards_geojson():
    global wards_gdf
    if wards_gdf is None:
        geojson_path = os.path.join(current_app.root_path, 'data', 'ghmc_wards.geojson')
        if not os.path.exists(geojson_path):
             raise FileNotFoundError(f"GeoJSON file not found at path: {geojson_path}")
        wards_gdf = gpd.read_file(geojson_path)
    return wards_gdf

# --- Authentication Routes ---
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user is None or not user.check_password(data.get('password')):
        return jsonify({'message': 'Invalid username or password'}), 401
    login_user(user)
    return jsonify({'message': 'Logged in successfully'}), 200

@bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/status', methods=['GET'])
def status():
    return jsonify({'logged_in': current_user.is_authenticated})

# --- NEW: Endpoint to get a list of all wards ---
@bp.route('/wards', methods=['GET'])
@login_required
def get_wards():
    try:
        wards_query = db.session.query(distinct(Post.ward)).filter(Post.ward.isnot(None)).order_by(Post.ward).all()
        wards = [ward[0] for ward in wards_query]
        return jsonify(wards)
    except Exception as e:
        print(f"Error fetching wards: {e}")
        return jsonify({"error": "Could not fetch ward list"}), 500

# --- UPGRADED: Main Analytics Endpoint (with all filters) ---
@bp.route('/analytics', methods=['GET'])
@login_required
def analytics():
    try:
        emotion_filter = request.args.get('emotion', 'All')
        city_filter = request.args.get('city', 'All')
        ward_filter = request.args.get('ward', 'All')
        search_filter = request.args.get('searchTerm', '')
        
        query = Post.query
        if emotion_filter != 'All': query = query.filter(Post.emotion == emotion_filter)
        if city_filter != 'All': query = query.filter(Post.city == city_filter)
        if ward_filter != 'All': query = query.filter(Post.ward == ward_filter)
        if search_filter: query = query.filter(Post.text.like(f"%{search_filter}%"))

        posts = query.all()
        return jsonify([p.to_dict() for p in posts])
    except Exception as e:
        print(f"Error in analytics endpoint: {e}")
        return jsonify({"error": "Failed to retrieve analytics data"}), 500

# --- Granular Analytics Route ---
@bp.route('/analytics/granular', methods=['GET'])
@login_required
def granular_analytics():
    try:
        wards = load_wards_geojson()
        posts = Post.query.filter(Post.latitude.isnot(None), Post.longitude.isnot(None)).all()
        if not posts: return jsonify({"type": "FeatureCollection", "features": []})

        ward_data = {row['name']: {'posts': [], 'geometry': row.geometry} for _, row in wards.iterrows()}

        for post in posts:
            # Use the pre-calculated ward if it exists
            if post.ward and post.ward in ward_data:
                ward_data[post.ward]['posts'].append(post)
        
        results = []
        for ward_name, data in ward_data.items():
            if not data['posts']:
                continue

            emotions = [p.emotion for p in data['posts'] if p.emotion]
            emotion_counts = Counter(emotions)
            dominant_emotion = emotion_counts.most_common(1)[0][0] if emotions else 'N/A'
            
            all_drivers = [driver for p in data['posts'] if p.drivers for driver in p.drivers]
            driver_counts = Counter(all_drivers)
            top_drivers = [driver[0] for driver in driver_counts.most_common(3)]
            
            results.append({
                "type": "Feature",
                "geometry": data['geometry'].__geo_interface__,
                "properties": {
                    "ward_name": ward_name,
                    "dominant_emotion": dominant_emotion,
                    "post_count": len(data['posts']),
                    "top_drivers": top_drivers
                }
            })
            
        return jsonify({
            "type": "FeatureCollection",
            "features": results
        })

    except Exception as e:
        print(f"Error in granular analytics: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An error occurred during geo-analysis"}), 500

# --- Strategic Summary Route ---
@bp.route('/strategic-summary', methods=['GET'])
@login_required
def strategic_summary():
    try:
        emotion_filter = request.args.get('emotion', 'All')
        city_filter = request.args.get('city', 'All')
        ward_filter = request.args.get('ward', 'All') # Also use ward filter here
        search_filter = request.args.get('searchTerm', '')

        query = Post.query
        if emotion_filter != 'All': query = query.filter(Post.emotion == emotion_filter)
        if city_filter != 'All': query = query.filter(Post.city == city_filter)
        if ward_filter != 'All': query = query.filter(Post.ward == ward_filter)
        if search_filter: query = query.filter(Post.text.like(f"%{search_filter}%"))
        
        filtered_posts = query.limit(100).all()

        if not filtered_posts or len(filtered_posts) < 2:
            return jsonify({"opportunity": "Not enough data for this filter.", "threat": "Please broaden your criteria.", "prescriptive_action": "Try selecting 'All' for filters."})

        top_emotion = pd.Series([p.emotion for p in filtered_posts]).mode()[0]
        
        all_drivers = [driver for p in filtered_posts if p.drivers for driver in p.drivers]
        top_drivers_text = ", ".join([d[0] for d in Counter(all_drivers).most_common(3)])
        
        news_context = "Recent local news reports indicate growing public concern over road quality and infrastructure projects, especially in high-traffic areas. This is becoming a key issue for the upcoming municipal elections."

        prompt = f"""
        You are an expert political strategist for a campaign in Hyderabad, India. Provide a clear, actionable intelligence briefing based on the following.

        **Intelligence:**
        - Dominant detected emotion: "{top_emotion}"
        - Key topics of discussion: "{top_drivers_text if top_drivers_text else 'General chatter'}"
        - Live News Context: "{news_context}"

        **Your Task:**
        Generate a strategic response in JSON format with three keys: "opportunity", "threat", and "prescriptive_action".
        Provide only the raw JSON object.
        """

        summary_json = generate_ai_response(prompt)
        return jsonify(summary_json)

    except Exception as e:
        print(f"Error in strategic summary: {e}")
        return jsonify({"error": "Failed to generate dynamic strategic summary."}), 500

def generate_ai_response(prompt):
    model = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        generation_config={"response_mime_type": "application/json"}
    )
    response = model.generate_content(prompt)
    return json.loads(response.text)