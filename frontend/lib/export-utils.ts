import jsPDF from "jspdf";
import * as XLSX from "xlsx";
import type { Property } from "./types";

export async function exportToCSV(
  data: Property[],
  filename: string
): Promise<void> {
  const headers = [
    "Title",
    "Price",
    "Price per SQM",
    "Location",
    "Bedrooms",
    "Bathrooms",
    "Type",
    "Source",
    "Timestamp",
  ];

  const csvContent = [
    headers.join(","),
    ...data.map((property) =>
      [
        `"${property.title}"`,
        property.price,
        property.price_per_sqm || "",
        `"${property.location}"`,
        property.bedrooms || "",
        property.bathrooms || "",
        `"${property.type || ""}"`,
        `"${property.source || ""}"`,
        `"${property.timestamp || ""}"`,
      ].join(",")
    ),
  ].join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");

  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `${filename}.csv`);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

export async function exportToXLSX(
  data: Property[],
  filename: string
): Promise<void> {
  const worksheet = XLSX.utils.json_to_sheet(
    data.map((property) => ({
      Title: property.title,
      Price: property.price,
      "Price per SQM": property.price_per_sqm || "",
      Location: property.location,
      Bedrooms: property.bedrooms || "",
      Bathrooms: property.bathrooms || "",
      Type: property.type || "",
      Source: property.source || "",
      Timestamp: property.timestamp || "",
    }))
  );

  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Properties");

  // Auto-size columns
  const colWidths = [
    { wch: 25 }, // Title
    { wch: 12 }, // Price
    { wch: 15 }, // Price per SQM
    { wch: 20 }, // Location
    { wch: 10 }, // Bedrooms
    { wch: 10 }, // Bathrooms
    { wch: 15 }, // Type
    { wch: 18 }, // Source
    { wch: 18 }, // Timestamp
  ];
  worksheet["!cols"] = colWidths;

  XLSX.writeFile(workbook, `${filename}.xlsx`);
}

export async function exportToPDF(
  data: Property[],
  filename: string
): Promise<void> {
  const pdf = new jsPDF("l", "mm", "a4"); // landscape orientation

  // Title
  pdf.setFontSize(16);
  pdf.setFont("helvetica", "bold");
  pdf.text("Property Data Export", 20, 20);

  // Date
  pdf.setFontSize(10);
  pdf.setFont("helvetica", "normal");
  pdf.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 30);

  // Table headers
  const headers = [
    "Title",
    "Price",
    "Location",
    "Bed",
    "Bath",
    "Type",
    "Source",
  ];
  const startY = 45;
  let currentY = startY;

  // Header row
  pdf.setFontSize(9);
  pdf.setFont("helvetica", "bold");
  let currentX = 20;
  const colWidths = [45, 25, 35, 15, 15, 25, 30];

  headers.forEach((header, index) => {
    pdf.text(header, currentX, currentY);
    currentX += colWidths[index];
  });

  // Draw header line
  pdf.line(20, currentY + 2, 270, currentY + 2);
  currentY += 8;

  // Data rows
  pdf.setFont("helvetica", "normal");
  pdf.setFontSize(8);

  data.forEach((property, index) => {
    if (currentY > 180) {
      // New page if needed
      pdf.addPage();
      currentY = 20;
    }

    currentX = 20;
    const rowData = [
      property.title.length > 30
        ? property.title.substring(0, 30) + "..."
        : property.title,
      typeof property.price === "number"
        ? `$${property.price.toLocaleString()}`
        : `${property.price}`,
      property.location.length > 25
        ? property.location.substring(0, 25) + "..."
        : property.location,
      (property.bedrooms || 0).toString(),
      (property.bathrooms || 0).toString(),
      property.type || "",
      (property.source || "").length > 20
        ? (property.source || "").substring(0, 20) + "..."
        : property.source || "",
    ];

    rowData.forEach((cell, cellIndex) => {
      pdf.text(cell || "", currentX, currentY);
      currentX += colWidths[cellIndex];
    });

    currentY += 6;

    // Add line every 5 rows for readability
    if ((index + 1) % 5 === 0) {
      pdf.line(20, currentY, 270, currentY);
      currentY += 2;
    }
  });

  // Footer
  const pageCount = pdf.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    pdf.setPage(i);
    pdf.setFontSize(8);
    pdf.text(`Page ${i} of ${pageCount}`, 250, 200);
    pdf.text(`Total Records: ${data.length}`, 20, 200);
  }

  pdf.save(`${filename}.pdf`);
}

// Utility function to format data for export
export function formatPropertyForExport(property: Property) {
  return {
    title: property.title,
    price: property.price,
    pricePerSqm: property.price_per_sqm,
    location: property.location,
    bedrooms: property.bedrooms,
    bathrooms: property.bathrooms,
    type: property.type,
    source: property.source,
    timestamp: property.timestamp,
  };
}

// Batch export function for large datasets
export async function batchExport(
  data: Property[],
  format: "csv" | "xlsx" | "pdf",
  filename: string,
  batchSize = 1000
): Promise<void> {
  if (data.length <= batchSize) {
    switch (format) {
      case "csv":
        return exportToCSV(data, filename);
      case "xlsx":
        return exportToXLSX(data, filename);
      case "pdf":
        return exportToPDF(data, filename);
    }
  }

  // For large datasets, split into batches
  const batches = [];
  for (let i = 0; i < data.length; i += batchSize) {
    batches.push(data.slice(i, i + batchSize));
  }

  for (let i = 0; i < batches.length; i++) {
    const batchFilename = `${filename}_batch_${i + 1}`;
    switch (format) {
      case "csv":
        await exportToCSV(batches[i], batchFilename);
        break;
      case "xlsx":
        await exportToXLSX(batches[i], batchFilename);
        break;
      case "pdf":
        await exportToPDF(batches[i], batchFilename);
        break;
    }
  }
}
