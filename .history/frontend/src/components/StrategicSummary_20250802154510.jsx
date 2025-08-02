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
        setError("Could not load AI strategic summary.");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) {
    return <div className="text-gray-500">🧠 Generating AI strategic briefing...</div>;
  }

  if (error || summary?.error) {
    return <div className="text-red-500">{error || summary.error}</div>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h4 className="font-semibold text-gray-800">High-Level Analysis</h4>
        <p className="text-gray-700 italic">"{summary?.analysis}"</p>
      </div>
      <hr/>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="font-semibold text-green-600">📈 Strategic Opportunity</h4>
          <p className="text-gray-700">{summary?.opportunity}</p>
        </div>
        <div>
          <h4 className="font-semibold text-red-600">⚠️ Strategic Threat</h4>
          <p className="text-gray-700">{summary?.threat}</p>
        </div>
      </div>
       <hr/>
      <div>
        <h4 className="font-semibold text-blue-600">📱 Suggested Social Media Response</h4>
        <div className="mt-2 p-3 bg-gray-50 rounded-md border border-gray-200">
            <p className="text-gray-800 whitespace-pre-wrap">{summary?.suggested_post}</p>
        </div>
      </div>
    </div>
  );
}

export default StrategicSummary;