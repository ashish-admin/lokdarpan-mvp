import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

const CENTER = [17.44, 78.47]; // Centered on Hyderabad
const ZOOM_LEVEL = 11;

// Define a consistent color scheme for emotions
const emotionColorMap = {
  Hope: '#2ecc71',     // Green
  Anger: '#e74c3c',    // Red
  Joy: '#3498db',      // Blue
  Anxiety: '#f1c40f',  // Yellow
  Sadness: '#9b59b6', // Purple
  Disgust: '#7f8c8d',  // Grey
  Apathy: '#bdc3c7',   // Lighter Grey
  Neutral: '#bdc3c7',  // Also Lighter Grey for apathy/neutral
  Error: '#e67e22',    // Orange
  Default: '#95a5a6'  // Default Grey for unknown
};

function LocationMap() {
  const [geoData, setGeoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGranularData = async () => {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || '';
      try {
        axios.defaults.withCredentials = true;
        const response = await axios.get(`${apiUrl}/api/v1/analytics/granular`);
        
        if (response.data && response.data.length > 0) {
            // Transform the API response into a valid GeoJSON FeatureCollection
            const geoJsonFeatures = {
              type: "FeatureCollection",
              features: response.data.map(ward => ({
                type: "Feature",
                geometry: ward.geometry,
                properties: {
                  name: ward.ward_name,
                  emotion: ward.dominant_emotion,
                  count: ward.post_count
                }
              }))
            };
            setGeoData(geoJsonFeatures);
        } else {
            // Handle cases where no data is returned
            setGeoData(null); 
        }

      } catch (err) {
        console.error("Failed to fetch granular map data:", err);
        setError("Could not load granular map data.");
      } finally {
        setLoading(false);
      }
    };

    fetchGranularData();
  }, []);

  // Function to determine the style of each ward polygon
  const getStyle = (feature) => {
    const emotion = feature.properties.emotion;
    return {
      fillColor: emotionColorMap[emotion] || emotionColorMap.Default,
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.7
    };
  };

  // Function to bind popups to each ward
  const onEachFeature = (feature, layer) => {
    if (feature.properties) {
      const { name, emotion, count } = feature.properties;
      const popupContent = `
        <b>Ward:</b> ${name}<br/>
        <b>Dominant Emotion:</b> ${emotion}<br/>
        <b>Post Count:</b> ${count}
      `;
      layer.bindPopup(popupContent);
    }
  };

  if (loading) {
    return <div className="text-center p-4">Loading map data...</div>;
  }
  
  if (error) {
    return <div className="text-center p-4 text-red-500">{error}</div>;
  }
  
  if (!geoData) {
    return <div className="text-center p-4">No granular data available to display on the map.</div>;
  }

  return (
    <div className="h-96 w-full rounded-lg overflow-hidden">
      <MapContainer
        center={CENTER}
        zoom={ZOOM_LEVEL}
        scrollWheelZoom={true} // This is the change
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeoJSON data={geoData} style={getStyle} onEachFeature={onEachFeature} />
      </MapContainer>
    </div>
  );
}

export default LocationMap;