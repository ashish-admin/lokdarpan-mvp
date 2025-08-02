import { useState, useEffect } from 'react';
import axios from 'axios';

function StrategicSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      const apiUrl = import.meta.env.VITE_API_BASE_URL || '';
      try {
        axios.defaults.withCredentials = true;
        const response = await axios.get(`${apiUrl}/api/v1/strategic-summary`);
        setSummary(response.data);
      } catch (err) {
        console.error("Failed to fetch strategic summary:", err);
        setError("Could not load strategic summary.");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) {
    return <div className="text-gray-500">Generating AI summary...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h4 className="font-semibold text-green-600">Opportunity</h4>
        <p className="text-gray-700">{summary?.opportunity || 'N/A'}</p>
      </div>
      <div>
        <h4 className="font-semibold text-red-600">Threat</h4>
        <p className="text-gray-700">{summary?.threat || 'N/A'}</p>
      </div>
    </div>
  );
}

export default StrategicSummary;