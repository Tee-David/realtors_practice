"use client";
import React from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "@/lib/hooks/useApi";

const DuplicatesPage: React.FC = () => {
  // Example: detect duplicates for demo listings (empty array)
  const { data, error, loading } = useApi(() => apiClient.detectDuplicates([]));

  return (
    <div className="max-w-2xl mx-auto p-8 bg-white rounded-xl shadow-lg mt-8">
      <h1 className="text-2xl font-bold mb-6 text-blue-700">
        Duplicate Properties
      </h1>
      {loading && <p className="text-gray-500">Detecting duplicates...</p>}
      {error && (
        <p className="text-red-500">
          Error:{" "}
          {typeof error === "object" && "message" in error
            ? (error as any).message
            : String(error)}
        </p>
      )}
      {data && Array.isArray(data.groups) && data.groups.length > 0 ? (
        <ul className="space-y-2">
          {data.groups.map((group: any, idx: number) => (
            <li key={idx} className="bg-blue-50 p-3 rounded-lg flex flex-col">
              <span className="font-medium text-blue-900">
                Hash: {group.hash}
              </span>
              <span className="text-gray-600">Count: {group.count}</span>
              <span className="text-gray-600">
                Listings: {group.listings.length}
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-400">No duplicates detected.</p>
      )}
    </div>
  );
};

export default DuplicatesPage;
