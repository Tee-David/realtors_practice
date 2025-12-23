"use client";
import React from "react";
import { apiClient } from "@/lib/api";
import { useApi } from "@/lib/hooks/useApi";

const PriceIntelligencePage: React.FC = () => {
  // Example: show price drops and stale listings
  const {
    data: drops,
    error: dropsError,
    loading: dropsLoading,
  } = useApi(() =>
    apiClient.getPriceDrops({ min_drop_percentage: 5, days: 30 })
  );
  const {
    data: stale,
    error: staleError,
    loading: staleLoading,
  } = useApi(() => apiClient.getStaleListings(30));

  return (
    <div className="max-w-3xl mx-auto p-8 bg-white rounded-xl shadow-lg mt-8">
      <h1 className="text-2xl font-bold mb-6 text-blue-700">
        Price Intelligence
      </h1>
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-2 text-gray-800">
          Recent Price Drops
        </h2>
        {dropsLoading && (
          <p className="text-gray-500">Loading price drops...</p>
        )}
        {dropsError && (
          <p className="text-red-500">
            Error:{" "}
            {typeof dropsError === "object" && "message" in dropsError
              ? (dropsError as any).message
              : String(dropsError)}
          </p>
        )}
        {drops && Array.isArray(drops) && drops.length > 0 ? (
          <ul className="space-y-2">
            {drops.map((drop: any, idx: number) => (
              <li
                key={idx}
                className="bg-blue-50 p-3 rounded-lg flex justify-between items-center"
              >
                <span className="font-medium text-blue-900">
                  {drop.property_id || drop.id}
                </span>
                <span className="text-green-700 font-bold">
                  ↓ {drop.drop_percentage}%
                </span>
                <span className="text-gray-600">
                  {drop.date || drop.timestamp}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-400">No recent price drops found.</p>
        )}
      </div>
      <div>
        <h2 className="text-lg font-semibold mb-2 text-gray-800">
          Stale Listings
        </h2>
        {staleLoading && (
          <p className="text-gray-500">Loading stale listings...</p>
        )}
        {staleError && (
          <p className="text-red-500">
            Error:{" "}
            {typeof staleError === "object" && "message" in staleError
              ? (staleError as any).message
              : String(staleError)}
          </p>
        )}
        {stale && Array.isArray(stale) && stale.length > 0 ? (
          <ul className="space-y-2">
            {stale.map((listing: any, idx: number) => (
              <li
                key={idx}
                className="bg-yellow-50 p-3 rounded-lg flex justify-between items-center"
              >
                <span className="font-medium text-yellow-900">
                  {listing.title || listing.id}
                </span>
                <span className="text-gray-600">
                  Last updated: {listing.last_updated || listing.updated_at}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-400">No stale listings found.</p>
        )}
      </div>
    </div>
  );
};

export default PriceIntelligencePage;
