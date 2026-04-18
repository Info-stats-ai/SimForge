// Shared TypeScript types for SimForge

// ── Scenario ──────────────────────────────────────────────────────────────

export type EnvironmentTemplate = 'warehouse_aisle' | 'warehouse_open_floor' | 'warehouse_loading_dock' | 'warehouse_cold_storage'
export type RobotPathType = 'left_turn_blind_corner' | 'right_turn_blind_corner' | 'straight_aisle' | 't_junction' | 'cross_intersection' | 'u_turn'
export type LightingPreset = 'normal' | 'low_light' | 'high_contrast' | 'flickering' | 'emergency'
export type CameraMode = 'overhead' | 'follow' | 'fixed_angle' | 'first_person' | 'multi_view'
export type ObstacleLevel = 'none' | 'low' | 'medium' | 'high' | 'extreme'
export type ScenarioStatus = 'draft' | 'compiled' | 'running' | 'completed' | 'failed'

export interface Scenario {
  id: string
  name: string
  description: string
  environment_template: EnvironmentTemplate
  robot_path_type: RobotPathType
  human_crossing_probability: number
  dropped_obstacle_level: ObstacleLevel
  blocked_aisle_enabled: boolean
  lighting_preset: LightingPreset
  camera_mode: CameraMode
  variant_count: number
  random_seed: number
  notes: string
  status: ScenarioStatus
  created_at: string
  updated_at: string
}
