const API_BASE = "http://127.0.0.1:8000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request(path, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new ApiError(
        body?.detail || `Request failed with status ${response.status}`,
        response.status
      );
    }
    return response.json();
  } catch (err) {
    if (err instanceof ApiError) throw err;
    // Network / CORS failure
    throw new ApiError(
      "Unable to reach the backend. Is it running on port 8000?",
      0
    );
  }
}

export const api = {
  /** POST /scan — start a new scan */
  startScan(url, authorized = false) {
    return request("/scan", {
      method: "POST",
      body: JSON.stringify({ url, authorized }),
    });
  },

  /** GET /scan/{id} — poll for status/results */
  getScanStatus(scanId) {
    return request(`/scan/${scanId}`);
  },

  /** GET /scans — list all scans */
  getScans() {
    return request("/scans");
  },

  /** GET /scans/history?target= */
  getScanHistory(target) {
    return request(`/scans/history?target=${encodeURIComponent(target)}`);
  },

  /** Returns the export URL (opened in a new tab by the caller) */
  exportUrl(scanId, format) {
    return `${API_BASE}/scan/${scanId}/export?format=${format}`;
  },
};
