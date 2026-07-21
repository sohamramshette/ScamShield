export const API_URL = import.meta.env.VITE_API_URL || "/api/v1";

interface RequestConfig extends RequestInit {
  data?: any;
}

export const api = {
  get: (endpoint: string, config: RequestConfig = {}) => request("GET", endpoint, config),
  post: (endpoint: string, data?: any, config: RequestConfig = {}) => request("POST", endpoint, { ...config, data }),
  put: (endpoint: string, data?: any, config: RequestConfig = {}) => request("PUT", endpoint, { ...config, data }),
  delete: (endpoint: string, config: RequestConfig = {}) => request("DELETE", endpoint, config),
};

async function request(method: string, endpoint: string, config: RequestConfig = {}) {
  const token = localStorage.getItem("token");
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(config.headers as Record<string, string> || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const isFormData = config.data instanceof FormData || (config.data && typeof config.data.append === 'function');
  const body = isFormData ? config.data : (config.data ? JSON.stringify(config.data) : undefined);

  if (isFormData) {
    // Let the browser set the Content-Type with the proper boundary
    delete headers["Content-Type"];
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...config,
    method,
    headers,
    body,
  });

  const responseData = await response.json().catch(() => ({}));

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/";
    }
    throw new Error(responseData?.error?.message || responseData?.detail || "An unexpected error occurred");
  }

  return responseData;
}
