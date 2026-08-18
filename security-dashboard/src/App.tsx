import React, { useState,} from "react"
import type {ChangeEvent, FormEvent } from "react";

interface Header {
  key: string;
  value: string;
}

interface PipelineConfig {
  sourceType: "API" | "Database" | "File";
  endpoint: string;
  method: "GET" | "POST" | "PUT";
  headers: Header[];
  authToken: string;
  schedule: "manual" | "hourly" | "daily";
  destination: "Data Lake" | "Warehouse" | "Dashboard";
}

const DataIngestionForm: React.FC = () => {
  const [formData, setFormData] = useState<PipelineConfig>({
    sourceType: "API",
    endpoint: "",
    method: "GET",
    headers: [{ key: "", value: "" }],
    authToken: "",
    schedule: "manual",
    destination: "Data Lake",
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value as any });
  };

  const handleHeaderChange = (index: number, field: keyof Header, value: string) => {
    const newHeaders = [...formData.headers];
    newHeaders[index][field] = value;
    setFormData({ ...formData, headers: newHeaders });
  };

  const addHeader = () => {
    setFormData({
      ...formData,
      headers: [...formData.headers, { key: "", value: "" }],
    });
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    console.log("Pipeline Config:", formData);
    // send to backend or save
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: "20px", maxWidth: "600px" }}>
      <h2>Data Ingestion Pipeline Config</h2>

      <label>
        Source Type:
        <select name="sourceType" value={formData.sourceType} onChange={handleChange}>
          <option value="API">API</option>
          <option value="Database">Database</option>
          <option value="File">File Upload</option>
        </select>
      </label>

      <label>
        Endpoint / Connection String:
        <input
          type="text"
          name="endpoint"
          value={formData.endpoint}
          onChange={handleChange}
          placeholder="https://api.example.com/data"
        />
      </label>

      <label>
        Method:
        <select name="method" value={formData.method} onChange={handleChange}>
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
        </select>
      </label>

      <div>
        <h4>Headers</h4>
        {formData.headers.map((header, index) => (
          <div key={index}>
            <input
              type="text"
              placeholder="Key"
              value={header.key}
              onChange={(e) => handleHeaderChange(index, "key", e.target.value)}
            />
            <input
              type="text"
              placeholder="Value"
              value={header.value}
              onChange={(e) => handleHeaderChange(index, "value", e.target.value)}
            />
          </div>
        ))}
        <button type="button" onClick={addHeader}>+ Add Header</button>
      </div>

      <label>
        Auth Token:
        <input
          type="text"
          name="authToken"
          value={formData.authToken}
          onChange={handleChange}
          placeholder="Bearer token"
        />
      </label>

      <label>
        Schedule:
        <select name="schedule" value={formData.schedule} onChange={handleChange}>
          <option value="manual">Manual</option>
          <option value="hourly">Hourly</option>
          <option value="daily">Daily</option>
        </select>
      </label>

      <label>
        Destination:
        <select name="destination" value={formData.destination} onChange={handleChange}>
          <option value="Data Lake">Data Lake</option>
          <option value="Warehouse">Warehouse</option>
          <option value="Dashboard">Dashboard</option>
        </select>
      </label>

      <button type="submit">Save Pipeline</button>
    </form>
  );
};

export default DataIngestionForm;
