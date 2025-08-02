import React from "react";

const DataTable = ({ data }) => (
  <div className="overflow-x-auto max-h-96"> {/* Increased max height */}
    <table className="min-w-full table-auto text-sm">
      <thead className="sticky top-0 bg-indigo-100 z-10">
        <tr>
          {/* Re-ordered for better readability */}
          <th className="px-3 py-2 text-left">Text</th>
          <th className="px-3 py-2 text-left">Emotion</th>
          <th className="px-3 py-2 text-left">Drivers</th> {/* NEW Column */}
          <th className="px-3 py-2 text-left">City</th>
          <th className="px-3 py-2 text-left">Timestamp</th>
        </tr>
      </thead>
      <tbody className="bg-white">
        {/* Make sure the data exists before mapping */}
        {data && data.map((row) => (
          <tr key={row.id} className="border-b border-gray-200 hover:bg-gray-50">
            <td className="px-3 py-2">{row.text}</td>
            <td className="px-3 py-2 font-semibold">{row.emotion}</td>
            {/* NEW: Display drivers, joined as a string */}
            <td className="px-3 py-2 italic text-gray-600">
                {row.drivers && row.drivers.length > 0 ? row.drivers.join(', ') : 'N/A'}
            </td>
            <td className="px-3 py-2">{row.city}</td>
            <td className="px-3 py-2">{row.timestamp}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default DataTable;