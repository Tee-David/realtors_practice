/**
 * React Hook for Exporting Firestore Data
 * Export listings to CSV, JSON, etc.
 */

import { useState } from 'react';
import { apiClient } from './api-client';

export interface ExportOptions {
  format: 'csv' | 'json' | 'excel';
  collection?: 'properties' | 'properties_archive';
  filters?: Record<string, any>;
  limit?: number;
}

/**
 * Hook for exporting Firestore data to files
 *
 * @example
 * ```tsx
 * const { exportData, isExporting, error } = useFirestoreExport();
 *
 * const handleExport = async () => {
 *   await exportData({ format: 'csv', limit: 1000 });
 * };
 * ```
 */
export function useFirestoreExport() {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const exportData = async (options: ExportOptions) => {
    setIsExporting(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/firestore/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          format: options.format,
          collection: options.collection || 'properties',
          filters: options.filters || {},
          limit: options.limit || 1000
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Export failed');
      }

      // Create download link
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // Set filename based on format
      const timestamp = new Date().toISOString().slice(0, 10);
      const extension = options.format === 'excel' ? 'xlsx' : options.format;
      a.download = `firestore_export_${timestamp}.${extension}`;

      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      return true;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Export failed');
      setError(error);
      return false;
    } finally {
      setIsExporting(false);
    }
  };

  return {
    exportData,
    isExporting,
    error
  };
}

/**
 * Example usage component
 */
export function ExportButton() {
  const { exportData, isExporting, error } = useFirestoreExport();

  const handleExportCSV = async () => {
    await exportData({
      format: 'csv',
      limit: 1000
    });
  };

  const handleExportJSON = async () => {
    await exportData({
      format: 'json',
      limit: 1000
    });
  };

  return (
    <div>
      <button onClick={handleExportCSV} disabled={isExporting}>
        {isExporting ? 'Exporting...' : 'Export as CSV'}
      </button>

      <button onClick={handleExportJSON} disabled={isExporting}>
        {isExporting ? 'Exporting...' : 'Export as JSON'}
      </button>

      {error && <div style={{ color: 'red' }}>{error.message}</div>}
    </div>
  );
}
