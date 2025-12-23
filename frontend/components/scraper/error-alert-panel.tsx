import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function ErrorAlertPanel() {
  const [errors, setErrors] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    apiClient
      .getErrorLogs(20)
      .then((data) => {
        setErrors(data.logs || []);
        setError(null);
      })
      .catch((err) => {
        setError(err.message || "Failed to fetch error logs");
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle>Error & Alert Center</CardTitle>
      </CardHeader>
      <CardContent>
        {loading && <div>Loading...</div>}
        {error && <div className="text-red-400">Error: {error}</div>}
        {!loading && !error && errors.length === 0 && (
          <div>No recent errors found.</div>
        )}
        <ul className="space-y-2 max-h-64 overflow-y-auto">
          {errors.map((err, idx) => (
            <li key={idx} className="border-b pb-2">
              <div className="flex justify-between items-center">
                <div>
                  <span className="text-red-400 font-semibold">
                    {err.level || "ERROR"}
                  </span>{" "}
                  {err.timestamp && new Date(err.timestamp).toLocaleString()}
                  <br />
                  <span className="text-xs text-slate-400">
                    {err.site_key || "system"}
                  </span>
                </div>
                <div className="text-slate-300 text-sm">{err.message}</div>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
