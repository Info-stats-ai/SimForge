// Shared TypeScript types — Evaluation

export interface EvaluationReport {
  id: string
  job_id: string
  collision_risk_score: number
  occlusion_score: number
  path_conflict_score: number
  severity_score: number
  diversity_score: number
  coverage_summary: Record<string, any>
  explanation: string
  top_risk_factors: string[]
  recommended_actions: string[]
  created_at: string
}
