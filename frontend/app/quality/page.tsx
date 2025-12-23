"use client";
import React from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "@/lib/hooks/useApi";

const QualityPage: React.FC = () => {
  // Example: score quality for demo property
  const demoProperty = {
    title: "Sample Property",
    price: 10000000,
    location: "Lekki",
  };
  const { data, error, loading } = useApi(() =>
    apiClient.scoreQuality(demoProperty)
  );

  return (
    <div className="max-w-xl mx-auto p-8 bg-white rounded-xl shadow-lg mt-8">
      <h1 className="text-2xl font-bold mb-6 text-blue-700">Quality Score</h1>
      {loading && <p className="text-gray-500">Scoring quality...</p>}
      {error && (
        <p className="text-red-500">
          Error:{" "}
          {typeof error === "object" && "message" in error
            ? (error as any).message
            : String(error)}
        </p>
      )}
      {data ? (
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="font-medium text-blue-900 mb-2">
            Score:{" "}
            <span className="text-green-700 font-bold">
              {data.score} / {data.max_score}
            </span>
          </div>
          <div className="text-gray-700 mb-2">
            Property: {data.property?.title} ({data.property?.location})
          </div>
          <div className="text-gray-700">
            <strong>Breakdown:</strong>
            <ul className="list-disc ml-6">
              {Object.entries(data.breakdown).map(([key, value]) => (
                <li key={key}>
                  {key.replace("has_", "").replace("_", " ")}: {value}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <p className="text-gray-400">No score available.</p>
      )}
    </div>
  );
};

export default QualityPage;
