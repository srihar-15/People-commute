const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "An error occurred";
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || JSON.stringify(errorJson);
    } catch (_) {
      errorDetail = response.statusText;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Auth
  login: async (email: string, password: string) => {
    return fetchAPI("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  register: async (data: any) => {
    return fetchAPI("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  me: async () => {
    return fetchAPI("/auth/me");
  },

  // Grievances
  listGrievances: async (filters: { status?: string; dept_id?: string } = {}) => {
    let params = new URLSearchParams();
    if (filters.status) params.append("status_filter", filters.status);
    if (filters.dept_id) params.append("dept_filter", filters.dept_id);
    const query = params.toString() ? `?${params.toString()}` : "";
    return fetchAPI(`/grievances/${query}`);
  },
  createGrievance: async (data: any) => {
    return fetchAPI("/grievances/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  getGrievanceDetail: async (id: string) => {
    return fetchAPI(`/grievances/${id}`);
  },
  acceptGrievance: async (id: string) => {
    return fetchAPI(`/grievances/${id}/accept`, {
      method: "POST",
    });
  },
  resolveGrievance: async (id: string, data: { evidence_url: string; notes: string }) => {
    return fetchAPI(`/grievances/${id}/resolve`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  confirmGrievance: async (id: string) => {
    return fetchAPI(`/grievances/${id}/confirm`, {
      method: "POST",
    });
  },
  rejectGrievance: async (id: string, notes: string) => {
    return fetchAPI(`/grievances/${id}/reject?reopen_notes=${encodeURIComponent(notes)}`, {
      method: "POST",
    });
  },
  adminRouteGrievance: async (id: string, department_id: string, priority: string = "MEDIUM") => {
    return fetchAPI(`/grievances/${id}/admin-review?department_id=${department_id}&priority=${priority}`, {
      method: "POST",
    });
  },
  mpEscalateGrievance: async (id: string, priority: string = "EMERGENCY", hours: number = 6) => {
    return fetchAPI(`/grievances/${id}/mp-escalate?priority=${priority}&hours_to_resolve=${hours}`, {
      method: "POST",
    });
  },
  getOfficerAssistant: async (id: string) => {
    return fetchAPI(`/grievances/${id}/assistant`);
  },

  // Analytics & RAG
  getKPIs: async () => {
    return fetchAPI("/analytics/kpi");
  },
  getHealthIndices: async () => {
    return fetchAPI("/analytics/health-index");
  },
  recalculateHealth: async () => {
    return fetchAPI("/analytics/recalculate", {
      method: "POST",
    });
  },
  policyChat: async (query: string) => {
    return fetchAPI("/analytics/policy-rag", {
      method: "POST",
      body: JSON.stringify({ query }),
    });
  },
};
