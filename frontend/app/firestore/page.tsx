"use client";
import React from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "@/lib/hooks/useApi";

const FirestorePage: React.FC = () => {
  const { data, error, loading } = useApi(() =>
    apiClient.queryFirestore({ limit: 10 })
  );

  return (
    <div className="max-w-2xl mx-auto p-8 bg-white rounded-xl shadow-lg mt-8">
      <h1 className="text-2xl font-bold mb-6 text-blue-700">Firestore Data</h1>
      {loading && <p className="text-gray-500">Loading Firestore data...</p>}
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
          {data.map((property: any, idx: number) => (
            <li key={idx} className="bg-blue-50 p-3 rounded-lg flex flex-col">
              <span className="font-medium text-blue-900">
                {property.title}
              </span>
              <span className="text-green-700 font-bold">
                ₦{property.price?.toLocaleString()}
              </span>
              <span className="text-gray-600">{property.location}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-400">No Firestore data found.</p>
      )}
    </div>
  );
};

export default FirestorePage;
