// frontend/src/components/LocationMap.jsx

import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

const CENTER = [17.44, 78.47]; // Centered on Hyderabad
const ZOOM_LEVEL = 11;

const emotionColorMap = {
  Hope: '#2ecc71',
  Anger: '#e74c3c',
  Joy: '#3498db',
  Anxiety: '#f1c40f',
  Sadness: '#9b59b6',
  Disgust: '#7f8c8d',
  Apathy: '#bdc3c7',
  Default: '#95a5a6'
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
        
        if (response.data && response.data.features) {
            setGeoData(response.data);
        } else {
            setGeoData(null); 
        }
      } catch (err) {
        console.error("Failed to fetch granular map data:", err);
        setError("Could not load map data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };
    fetchGranularData();
  }, []);

  const getStyle = (feature) => {
    const emotion = feature.properties.dominant_emotion;
    return {
      fillColor: emotionColorMap[emotion] || emotionColorMap.Default,
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.75
    };
  };

  const onEachFeature = (feature, layer) => {
    if (feature.properties) {
      const { ward_name, dominant_emotion, post_count, top_drivers } = feature.properties;
      
      // ** NEW: Build the drivers list for the popup **
      let driversHtml = 'No specific drivers identified.';
      if (top_drivers && top_drivers.length > 0) {
        driversHtml = `<ul class="list-disc list-inside mt-1">${top_drivers.map(driver => `<li>${driver}</li>`).join('')}</ul>`;
      }

      const popupContent = `
        <div class="p-1">
          <h3 class="font-bold text-lg">${ward_name}</h3>
          <p><b>Dominant Emotion:</b> ${dominant_emotion}</p>
          <p><b>Post Count:</b> ${post_count}</p>
          <hr class="my-1"/>
          <p class="font-semibold">Top Drivers:</p>
          ${driversHtml}
        </div>
      `;
      layer.bindPopup(popupContent);
    }
  };

  if (loading) return <div className="text-center p-4">Loading map data...</div>;
  if (error) return <div className="text-center p-4 text-red-500">{error}</div>;
  if (!geoData) return <div className="text-center p-4">No granular data to display.</div>;

  return (
    <div className="h-96 w-full rounded-lg overflow-hidden shadow-inner">
      <MapContainer
        center={CENTER}
        zoom={ZOOM_LEVEL}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {/* Key prop is important for re-rendering when data changes */}
        <GeoJSON key={JSON.stringify(geoData)} data={geoData} style={getStyle} onEachFeature={onEachFeature} />
      </MapContainer>
    </div>
  );
}

export default LocationMap;