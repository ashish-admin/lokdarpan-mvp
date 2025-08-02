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
from sqlalchemy import distinct # <-- Make sure this is imported

# The blueprint must be named 'api' and have the correct url_prefix
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
        # Query the database for unique, non-null ward names
        wards_query = db.session.query(distinct(Post.ward)).filter(Post.ward.isnot(None)).order_by(Post.ward).all()
        wards = [ward[0] for ward in wards_query]
        return jsonify(wards)
    except Exception as e:
        print(f"Error fetching wards: {e}")
        return jsonify({"error": "Could not fetch ward list"}), 500

# --- Main Analytics Endpoint (with ward filtering) ---
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
        
# --- Granular & Strategic Routes (no changes needed) ---
# ... (granular_analytics, strategic_summary, and generate_ai_response functions remain the same) ...