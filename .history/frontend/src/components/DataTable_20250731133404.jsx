import React from "react";

const DataTable = ({ data }) => (
  <div className="overflow-x-auto max-h-80">
    <table className="min-w-full table-auto text-sm">
      <thead>
        <tr className="bg-indigo-100">
          <th className="px-2 py-1">ID</th>
          <th className="px-2 py-1">Timestamp</th>
          <th className="px-2 py-1">Text</th>
          <th className="px-2 py-1">City</th>
          <th className="px-2 py-1">Latitude</th>
          <th className="px-2 py-1">Longitude</th>
          <th className="px-2 py-1">Emotion</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr key={row.id} className="border-b">
            <td className="px-2 py-1">{row.id}</td>
            <td className="px-2 py-1">{row.timestamp}</td>
            <td className="px-2 py-1">{row.text}</td>
            <td className="px-2 py-1">{row.city}</td>
            <td className="px-2 py-1">{row.latitude}</td>
            <td className="px-2 py-1">{row.longitude}</td>
            <td className="px-2 py-1 font-semibold">
              {row.emotion}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default DataTable;