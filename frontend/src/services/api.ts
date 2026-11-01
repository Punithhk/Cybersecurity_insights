import axios from 'axios';
import { useState, useEffect } from 'react';

export interface LogEvent {
  id?: number;
  class_uid: number;
  category_uid: number;
  severity: string;
  raw_payload: Record<string, any>;
  created_at?: string;
}

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getOpenCVELogs = async (): Promise<LogEvent[]> => {
  const response = await apiClient.get<LogEvent[]>('/opencve/');
  return response.data;
};

export const triggerOpenCVEIngest = async (): Promise<any> => {
  const response = await apiClient.post('/opencve/sync');
  return response.data;
};

export const triggerTrivyScan = async (): Promise<any> => {
  const response = await apiClient.post('/trivy/scan-local');
  return response.data;
};

export const triggerSuricataIngest = async (): Promise<any> => {
  const response = await apiClient.post('/suricata/ingest-logs');
  return response.data;
};

export function useSecurityData() {
  const [logs, setLogs] = useState<LogEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLogsData = async () => {
    try {
      setLoading(true);
      const data = await getOpenCVELogs();
      setLogs(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Network Error: Make sure FastAPI is running on port 8000');
    } finally {
      setLoading(false);
    }
  };

  const runOpenCVEIngest = async () => {
    setActionLoading(true);
    try {
      await triggerOpenCVEIngest();
      await fetchLogsData();
    } catch (err) {
      alert("Error triggering OpenCVE ingestion.");
    } finally {
      setActionLoading(false);
    }
  };

  const runTrivyScan = async () => {
    setActionLoading(true);
    try {
      await triggerTrivyScan();
      await fetchLogsData();
    } catch (err) {
      alert("Error running Trivy scan or lock conflict.");
    } finally {
      setActionLoading(false);
    }
  };

  const runSuricataIngest = async () => {
    setActionLoading(true);
    try {
      await triggerSuricataIngest();
      await fetchLogsData();
    } catch (err) {
      alert("Error ingesting Suricata logs.");
    } finally {
      setActionLoading(false);
    }
  };

  useEffect(() => {
    fetchLogsData();
  }, []);

  return {
    logs,
    loading,
    actionLoading,
    error,
    refetch: fetchLogsData,
    runOpenCVEIngest,
    runTrivyScan,
    runSuricataIngest,
  };
}