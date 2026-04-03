import { apiClient } from './client'
import type {
  AuthTokens, User, FarmerGroup, FarmerProfile, FarmerScore,
  GroupScore, LoanCeiling, OverviewStats, ScoreBand, PaginatedResponse,
} from '@/types'

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (username: string, password: string) =>
    apiClient.post<AuthTokens & { user: User }>('/auth/login/', { username, password }),
  logout: (refresh: string) =>
    apiClient.post('/auth/logout/', { refresh }),
  me: () =>
    apiClient.get<User>('/auth/me/'),
}

// ── Groups ───────────────────────────────────────────────────────────────────
export const groupsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<FarmerGroup>>('/groups/', { params }),
  detail: (id: string) =>
    apiClient.get<FarmerGroup>(`/groups/${id}/`),
  create: (data: Partial<FarmerGroup>) =>
    apiClient.post<FarmerGroup>('/groups/', data),
  update: (id: string, data: Partial<FarmerGroup>) =>
    apiClient.patch<FarmerGroup>(`/groups/${id}/`, data),
  approve: (id: string) =>
    apiClient.post(`/groups/${id}/approve/`),
  score: (id: string) =>
    apiClient.get<GroupScore>(`/groups/${id}/score/`),
  loanCeiling: (id: string) =>
    apiClient.get(`/groups/${id}/loan-ceiling/`),
  impactComparison: (id: string) =>
    apiClient.get(`/groups/${id}/impact/comparison/`),
}

// ── Farmers ──────────────────────────────────────────────────────────────────
export const farmersApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<FarmerProfile>>('/farmers/', { params }),
  detail: (id: string) =>
    apiClient.get<FarmerProfile>(`/farmers/${id}/`),
  create: (data: Partial<FarmerProfile>) =>
    apiClient.post<FarmerProfile>('/farmers/', data),
  update: (id: string, data: Partial<FarmerProfile>) =>
    apiClient.patch<FarmerProfile>(`/farmers/${id}/`, data),
  approve: (id: string) =>
    apiClient.post(`/farmers/${id}/approve/`),
  latestScore: (id: string) =>
    apiClient.get<FarmerScore>(`/farmers/${id}/scores/latest/`),
  calculateScore: (id: string) =>
    apiClient.post(`/farmers/${id}/scores/calculate/`),
  latestLoanCeiling: (id: string) =>
    apiClient.get<LoanCeiling>(`/farmers/${id}/loan-ceiling/latest/`),
  calculateLoanCeiling: (id: string, policyId?: string) =>
    apiClient.post(`/farmers/${id}/loan-ceiling/calculate/`, { policy_id: policyId }),
  crops: (id: string) =>
    apiClient.get(`/farmers/${id}/crops/`),
  addCrop: (id: string, data: unknown) =>
    apiClient.post(`/farmers/${id}/crops/`, data),
  plots: (id: string) =>
    apiClient.get(`/farmers/${id}/plots/`),
}

// ── Analytics ────────────────────────────────────────────────────────────────
export const analyticsApi = {
  overview: () =>
    apiClient.get<OverviewStats>('/analytics/overview/'),
  scoreDistribution: () =>
    apiClient.get<ScoreBand[]>('/analytics/score-distribution/'),
  cropIntelligence: () =>
    apiClient.get('/analytics/crop-intelligence/'),
  groupMap: () =>
    apiClient.get('/analytics/groups/map/'),
  districtProfile: (district: string) =>
    apiClient.get(`/analytics/district/${district}/`),
  agentPerformance: () =>
    apiClient.get('/analytics/agent-performance/'),
  impactSummary: () =>
    apiClient.get('/analytics/impact-summary/'),
}

// ── Parameters ───────────────────────────────────────────────────────────────
export const parametersApi = {
  crops: () =>
    apiClient.get('/parameters/crops/'),
  updateCrop: (id: string, data: unknown) =>
    apiClient.patch(`/parameters/crops/${id}/`, data),
  cii: () =>
    apiClient.get('/parameters/cii/'),
  loanPolicies: () =>
    apiClient.get('/parameters/loan-policy/'),
  auditLog: () =>
    apiClient.get('/parameters/audit-log/'),
}

// ── Reports ──────────────────────────────────────────────────────────────────
export const reportsApi = {
  farmerCredit: (farmerId: string) =>
    apiClient.post(`/reports/farmer-credit/${farmerId}/`, {}, { responseType: 'blob' }),
  groupCredit: (groupId: string) =>
    apiClient.post(`/reports/group-credit/${groupId}/`, {}, { responseType: 'blob' }),
  cropIntelligenceExcel: () =>
    apiClient.get('/reports/crop-intelligence/export/', { responseType: 'blob' }),
  unbankedFarmers: () =>
    apiClient.get('/reports/unbanked-farmers/export/', { responseType: 'blob' }),
}
