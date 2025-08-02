// frontend/src/components/Dashboard.jsx

import EmotionChart from './EmotionChart';
import LocationMap from './LocationMap';
import DataTable from './DataTable';
import StrategicSummary from './StrategicSummary';

// Make sure to receive the 'allData' prop
function Dashboard({ data, allData, wards, filters, setFilters, searchTerm, setSearchTerm }) {

  // **FIX**: Use the `allData` prop to generate the list of options.
  // This ensures the dropdowns contain all possible options, not just the filtered ones.
  const emotions = ['All', ...new Set((allData || []).map(item => item.emotion))];
  const cities = ['All', ...new Set((allData || []).map(item => item.city))];

  const handleFilterChange = (e) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-4 rounded-lg shadow-md">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 items-end">
          {/* Emotion Dropdown */}
          <div>
            <label htmlFor="emotion" className="block text-sm font-medium text-gray-700">Emotion</label>
            <select
              id="emotion"
              name="emotion"
              value={filters.emotion}
              onChange={handleFilterChange}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              {emotions.map(e => <option key={e} value={e}>{e}</option>)}
            </select>
          </div>

          {/* City Dropdown */}
          <div>
            <label htmlFor="city" className="block text-sm font-medium text-gray-700">City</label>
            <select
              id="city"
              name="city"
              value={filters.city}
              onChange={handleFilterChange}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              {cities.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          {/* Ward Dropdown */}
          <div>
            <label htmlFor="ward" className="block text-sm font-medium text-gray-700">Ward</label>
            <select
              id="ward"
              name="ward"
              value={filters.ward}
              onChange={handleFilterChange}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              {Array.isArray(wards) && wards.map(w => <option key={w} value={w}>{w}</option>)}
            </select>
          </div>

          {/* Search Input */}
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">Keyword Search</label>
            <input
              type="text"
              id="search"
              name="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="e.g., roads, festival"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
        </div>
      </div>
      
      {/* Rest of the Dashboard components */}
      {/* ... */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-3 bg-white p-4 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Strategic Briefing</h3>
          <StrategicSummary filters={filters} searchTerm={searchTerm} />
        </div>

        <div className="lg:col-span-2 bg-white p-4 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Granular Emotion Map (GHMC Wards)</h3>
          <LocationMap />
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Overall Emotion Distribution</h3>
          {/* Use the main 'data' prop here, which represents the filtered data */}
          <EmotionChart data={data} />
        </div>

        <div className="lg:col-span-3 bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Data View ({data.length} results)</h3>
          {/* Use the main 'data' prop here as well */}
          <DataTable data={data} />
        </div>
      </div>

    </div>
  );
}

export default Dashboard;