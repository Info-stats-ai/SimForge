/**
 * SimForge shared configuration constants and environment helpers.
 */

export const API_BASE_URL = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api'

export const JOB_STATUS_COLORS: Record<string, string> = {
  queued: '#6366f1',
  preparing: '#f59e0b',
  running: '#3b82f6',
  rendering: '#8b5cf6',
  completed: '#10b981',
  failed: '#ef4444',
}

export const JOB_STATUS_LABELS: Record<string, string> = {
  queued: 'Queued',
  preparing: 'Preparing',
  running: 'Running',
  rendering: 'Rendering',
  completed: 'Completed',
  failed: 'Failed',
}

export const ENVIRONMENT_TEMPLATES = [
  { value: 'warehouse_aisle', label: 'Warehouse Aisle' },
  { value: 'warehouse_open_floor', label: 'Open Floor' },
  { value: 'warehouse_loading_dock', label: 'Loading Dock' },
  { value: 'warehouse_cold_storage', label: 'Cold Storage' },
]

export const ROBOT_PATH_TYPES = [
  { value: 'left_turn_blind_corner', label: 'Left Turn (Blind Corner)' },
  { value: 'right_turn_blind_corner', label: 'Right Turn (Blind Corner)' },
  { value: 'straight_aisle', label: 'Straight Aisle' },
  { value: 't_junction', label: 'T-Junction' },
  { value: 'cross_intersection', label: 'Cross Intersection' },
  { value: 'u_turn', label: 'U-Turn' },
]

export const LIGHTING_PRESETS = [
  { value: 'normal', label: 'Normal' },
  { value: 'low_light', label: 'Low Light' },
  { value: 'high_contrast', label: 'High Contrast' },
  { value: 'flickering', label: 'Flickering' },
  { value: 'emergency', label: 'Emergency' },
]

export const CAMERA_MODES = [
  { value: 'overhead', label: 'Overhead' },
  { value: 'follow', label: 'Follow' },
  { value: 'fixed_angle', label: 'Fixed Angle' },
  { value: 'first_person', label: 'First Person' },
  { value: 'multi_view', label: 'Multi-View' },
]

export const OBSTACLE_LEVELS = [
  { value: 'none', label: 'None' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'extreme', label: 'Extreme' },
]
