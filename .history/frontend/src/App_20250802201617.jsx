import { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import LoginPage from './components/LoginPage';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loadingAuth, setLoadingAuth] = useState(true);

  // Ensure initial state is always an empty array
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
    setError(null);
  };

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
      setAnalyticsData([]); // Clear data on logout
      setWards([]);
      return;
    }

    const fetchData = async () => {
      setLoadingData(true);
      setError(null);
      try {
        // Fetch wards list first, or in parallel
        const wardsResponse = await axios.get(`${apiUrl}/api/v1/wards`);
        if (Array.isArray(wardsResponse.data)) {
          setWards(['All', ...wardsResponse.data]);
        }

        // Then fetch the analytics data based on filters
        const analyticsResponse = await axios.get(`${apiUrl}/api/v1/analytics`, { params: { ...filters, searchTerm } });
        setAnalyticsData(Array.isArray(analyticsResponse.data) ? analyticsResponse.data : []);

      } catch (err) {
        console.error("Data fetching error:", err);
        setError('Failed to fetch dashboard data.');
        if (err.response && (err.response.status === 401 || err.response.status === 403)) {
          setIsLoggedIn(false);
        }
      } finally {
        setLoadingData(false);
      }
    };

    fetchData();
  }, [isLoggedIn, filters, searchTerm]);


  if (loadingAuth) {
    return <div className="flex justify-center items-center h-screen text-2xl">Authenticating...</div>;
  }

  if (!isLoggedIn) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  // Pass an empty array to `allData` if it's not ready yet to prevent crashes
  const allDataForFilters = analyticsData || [];

  return (
    <div className="bg-gray-100 min-h-screen">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">LokDarpan: Discourse Analytics</h1>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {loadingData && <div className="text-center p-2">Updating data...</div>}
          <Dashboard
            data={analyticsData}
            allData={allDataForFilters} // Pass the safe array for generating filter options
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