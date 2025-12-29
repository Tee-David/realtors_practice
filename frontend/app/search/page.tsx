"use client";
import React, { useState, useEffect } from "react";
import { useSWRProperties } from "@/lib/hooks/useSWRProperties";
import DataTable from "@/components/data/data-table";

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState("");
  const { properties, loading, error } = useSWRProperties(
    query ? { query } : {}
  );

  return (
    <div className="max-w-4xl mx-auto p-8 bg-white rounded-xl shadow-lg mt-8">
      <h1 className="text-2xl font-bold mb-6 text-blue-700">Property Search</h1>
      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for properties (e.g. 3 bedroom flat in Lekki)"
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      {loading && <p className="text-gray-500">Loading properties...</p>}
      {error && (
        <p className="text-red-500 mb-4">
          Error:{" "}
          {typeof error === "object" && "message" in error
            ? (error as any).message
            : String(error)}
        </p>
      )}
      {!loading && properties.length === 0 && (
        <div className="bg-slate-100 border border-slate-200 rounded-lg p-6 text-center text-slate-500 mt-8">
          <p className="text-lg font-medium mb-2">No properties found.</p>
          <p className="text-sm mb-2">Try a different search, or</p>
          <button
            onClick={() =>
              window.dispatchEvent(
                new CustomEvent("navigate", { detail: { page: "scraper" } })
              )
            }
            className="inline-block mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition cursor-pointer"
          >
            Run a Scrape in Scraper Control
          </button>
        </div>
      )}
      {properties.length > 0 && <DataTable properties={properties} />}
    </div>
  );
};

export default SearchPage;
