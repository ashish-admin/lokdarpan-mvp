import { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import LoginPage from './components/LoginPage';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loadingAuth, setLoadingAuth] = useState(true);

  const [analyticsData, setAnalyticsData] = useState([]);
  const [wards, setWards] = useState([]);
  const [loadingData, setLoadingData] = useState(false);
  const [error, setError] = useState(null);

  const [filters, setFilters] = useState({ emotion: 'All', city: 'All', ward: 'All' });
  const [searchTerm, setSearchTerm] = useState('');

  const apiUrl = import.meta.env.VITE_API_BASE_URL || '';
  axios.defaults.withCredentials = true;

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    setError(null); // Clear any previous errors on new login
  };

  // This single useEffect handles ALL data fetching and filtering.
  useEffect(() => {
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
    checkAuthStatus();
  }, []);

  useEffect(() => {
    if (!isLoggedIn) {
      setAnalyticsData([]);
      setWards([]);
      return;
    }

    const fetchData = async () => {
      setLoadingData(true);
      setError(null);
      try {
        const [analyticsResponse, wardsResponse] = await Promise.all([
          axios.get(`${apiUrl}/api/v1/analytics`, { params: { ...filters, searchTerm } }),
          axios.get(`${apiUrl}/api/v1/wards`)
        ]);

        // Defensive check: ensure analytics data is an array
        setAnalyticsData(Array.isArray(analyticsResponse.data) ? analyticsResponse.data : []);

        // Defensive check: ensure wards data is an array before setting state
        if (Array.isArray(wardsResponse.data)) {
            setWards(['All', ...wardsResponse.data]);
        }
        
      } catch (err) {
        console.error("Data fetching error:", err); // Log the full error
        setError('Failed to fetch dashboard data.');

        // **ROBUST ERROR HANDLING**: Check if err.response exists before accessing status
        if (err.response && (err.response.status === 401 || err.response.status === 403)) {
          setIsLoggedIn(false); // Log out if session is invalid
        }
      } finally {
        setLoadingData(false);
      }
    };

    fetchData();
  }, [isLoggedIn, filters, searchTerm]);

  // --- UI RENDERING LOGIC ---

  if (loadingAuth) {
    return <div className="flex justify-center items-center h-screen text-2xl">Authenticating...</div>;
  }

  if (!isLoggedIn) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  // Show a loading screen only on the initial fetch
  if (loadingData && analyticsData.length === 0) {
    return <div className="flex justify-center items-center h-screen text-2xl">Loading Dashboard...</div>;
  }

  // Always show a clear error message if something went wrong
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
          {/* We can add a small loading indicator for subsequent loads */}
          {loadingData && <div className="text-center p-2">Updating data...</div>}
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