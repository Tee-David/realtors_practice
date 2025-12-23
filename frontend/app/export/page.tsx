"use client";
import React from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "@/lib/hooks/useApi";

const ExportPage: React.FC = () => {
  const { data, error, loading } = useApi(() => apiClient.getExportFormats());

  return (
    <div className="max-w-xl mx-auto p-8 bg-white rounded-xl shadow-lg mt-8">
      <h1 className="text-2xl font-bold mb-6 text-blue-700">Export Data</h1>
      {loading && <p className="text-gray-500">Loading export formats...</p>}
      {error && (
        <p className="text-red-500">
          Error:{" "}
          {typeof error === "object" && "message" in error
            ? (error as any).message
            : String(error)}
        </p>
      )}
      {data && Array.isArray(data) && data.length > 0 ? (
        <ul className="space-y-2">
          {data.map((format: string, idx: number) => (
            <li
              key={idx}
              className="bg-blue-50 p-3 rounded-lg flex justify-between items-center"
            >
              <span className="font-medium text-blue-900">{format}</span>
              <button className="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Download
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-400">No export formats available.</p>
      )}
    </div>
  );
};

export default ExportPage;
