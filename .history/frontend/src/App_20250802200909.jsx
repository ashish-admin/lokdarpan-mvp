import { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import LoginPage from './components/LoginPage';

function App() {
  // --- STATE MANAGEMENT (No changes here) ---
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loadingAuth, setLoadingAuth] = useState(true);

  const [analyticsData, setAnalyticsData] = useState([]);
  const [wards, setWards] = useState([]);
  const [loadingData, setLoadingData] = useState(false); // Default to false
  const [error, setError] = useState(null);

  const [filters, setFilters] = useState({ emotion: 'All', city: 'All', ward: 'All' });
  const [searchTerm, setSearchTerm] = useState('');

  const apiUrl = import.meta.env.VITE_API_BASE_URL || '';
  axios.defaults.withCredentials = true;

  // --- AUTHENTICATION LOGIC (No changes here) ---
  const checkAuthStatus = async () => {
    setLoadingAuth(true);
    try {
      const response = await axios.get(`${apiUrl}/api/v1/status`);
      setIsLoggedIn(response.data.logged_in);
    } catch (err) {
      setIsLoggedIn(false);
    } finally {
      setLoadingAuth(false);
    }
  };

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };

  // --- DATA FETCHING LOGIC (This is the corrected part) ---

  // Initial auth check on component mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  // This single useEffect handles ALL data fetching and filtering.
  // It runs ONLY when isLoggedIn, filters, or searchTerm change.
  useEffect(() => {
    // Do not fetch data if the user is not logged in.
    if (!isLoggedIn) {
      setAnalyticsData([]); // Clear data on logout
      return;
    }

    const fetchData = async () => {
      setLoadingData(true);
      setError(null);
      try {
        // We can fetch wards list once and reuse, but for simplicity, we fetch it with analytics
        const [analyticsResponse, wardsResponse] = await Promise.all([
          axios.get(`${apiUrl}/api/v1/analytics`, { params: { ...filters, searchTerm } }),
          axios.get(`${apiUrl}/api/v1/wards`)
        ]);

        setAnalyticsData(analyticsResponse.data);
        // Only set wards if it hasn't been set before to avoid dropdown flicker
        if (wards.length === 0) {
          setWards(['All', ...wardsResponse.data]);
        }
        
      } catch (err) {
        setError('Failed to fetch dashboard data.');
        console.error("Data fetching error:", err);
        // If an API call fails (e.g., session expired), log the user out
        if (err.response && (err.response.status === 401 || err.response.status === 403)) {
            setIsLoggedIn(false);
        }
      } finally {
        setLoadingData(false);
      }
    };

    fetchData();
  }, [isLoggedIn, filters, searchTerm]); // Dependencies are now clean and explicit

  // --- UI RENDERING LOGIC (No changes here) ---

  if (loadingAuth) {
    return <div className="flex justify-center items-center h-screen text-2xl">Checking Authentication...</div>;
  }

  if (!isLoggedIn) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  if (loadingData && analyticsData.length === 0) { // Only show full loading screen on initial data load
    return <div className="flex justify-center items-center h-screen text-2xl">Loading Dashboard...</div>;
  }

  if (error) {
    return <div className="flex justify-center items-center h-screen text-2xl text-red-500">{error}</div>;
  }

  return (
    <div className="bg-gray-100 min-h-screen">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">LokDarpan: Discourse Analytics</h1>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Dashboard
            data={analyticsData}
            wards={wards}
            filters={filters}
            setFilters={setFilters}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
          />
        </div>
      </main>
    </div>
  );
}

export default App;