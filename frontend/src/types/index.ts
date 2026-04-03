// ── Auth ────────────────────────────────────────────────────────────────────

export type UserRole =
  | 'system_admin'
  | 'field_agent'
  | 'supervisor'
  | 'analyst'
  | 'partner_user'
  | 'executive'

export interface User {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  role: UserRole
  phone: string
  district: string
  organisation: string
  is_active: boolean
  last_sync: string | null
  date_joined: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

// ── Groups ───────────────────────────────────────────────────────────────────

export type GroupType = 'vsla' | 'rosca' | 'sacco' | 'cooperative' | 'farmers_group' | 'other'

export interface FarmerGroup {
  id: string
  name: string
  group_type: GroupType
  district: string
  sub_county: string
  village: string
  parish: string
  is_registered: boolean
  is_approved: boolean
  member_count: number
  total_land_acres: number
  gacs: number | null
  chairperson_name: string
  chairperson_phone: string
  has_bank_account: boolean
  has_mobile_money: boolean
  gps_meeting_point: GeoJSONPoint | null
  created_at: string
}

// ── Farmers ──────────────────────────────────────────────────────────────────

export interface FarmerProfile {
  id: string
  group: string
  group_name: string
  full_name: string
  national_id: string
  gender: 'male' | 'female' | 'other'
  district: string
  primary_phone: string
  submission_status: 'pending' | 'approved' | 'rejected'
  is_active: boolean
  profile_completeness: number
  dependant_ratio: number
  household_size: number
  prior_loan_status: '' | 'repaid' | 'ongoing' | 'defaulted'
  created_at: string
}

export interface FarmerCrop {
  id: string
  farmer: string
  crop_name: string
  crop_category: 'subsistence' | 'cash' | 'both'
  season: 'season_a' | 'season_b' | 'both' | 'perennial'
  planting_month: number
  harvest_month: number
  acreage: number
  seed_source: 'certified' | 'saved' | 'market'
  uses_inputs: boolean
  expected_yield_kg_per_acre: number
  sell_to: string
  seasons_farmed: number
  post_harvest_loss_pct: number
}

// ── Scores ───────────────────────────────────────────────────────────────────

export type CreditBand = 'platinum' | 'gold' | 'silver' | 'bronze' | 'unscored'

export interface FarmerScore {
  id: string
  farmer: string
  acs_with_saf: number
  acs_score: number
  credit_band: CreditBand
  ivs_score: number
  las_score: number
  cps_score: number
  gss_score: number
  fbs_score: number
  hss_score: number
  cii_multiplier: number
  risk_flags: RiskFlag[]
  calculated_at: string
}

export interface RiskFlag {
  level: 'red' | 'amber'
  message: string
}

export interface GroupScore {
  id: string
  group: string
  group_name: string
  gacs_score: number
  avg_acs_score: number
  credit_band: CreditBand
  member_count: number
  total_land_acres: number
  calculated_at: string
}

// ── Loans ────────────────────────────────────────────────────────────────────

export interface LoanCeiling {
  id: string
  farmer: string
  farmer_name: string
  loan_ceiling_ugx: number
  loan_ceiling_ugx_formatted: string
  agricultural_surplus_ugx: number
  net_farm_income_ugx: number
  household_expenditure_ugx: number
  disbursement_month: number
  repayment_start_month: number
  recommended_loan_term_months: number
  applicable_interest_rate: number
  crop_calculations: CropCalculation[]
  calculated_at: string
}

export interface CropCalculation {
  crop_name: string
  acreage: number
  yield_per_acre: number
  reliability_factor: number
  farm_gate_price: number
  gross_revenue: number
  realised_revenue: number
  total_costs: number
}

// ── Analytics ────────────────────────────────────────────────────────────────

export interface OverviewStats {
  total_farmers: number
  total_groups: number
  districts_covered: number
  avg_acs_score: number
  pending_submissions: number
}

export interface ScoreBand {
  credit_band: CreditBand
  count: number
}

// ── Shared ───────────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  total_pages: number
  current_page: number
  results: T[]
}

export interface GeoJSONPoint {
  type: 'Point'
  coordinates: [number, number]  // [lon, lat]
}
