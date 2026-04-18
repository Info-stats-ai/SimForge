<template>
  <div class="max-w-4xl mx-auto space-y-8">
    <!-- Progress Steps -->
    <div class="flex items-center justify-center gap-2 mb-2">
      <template v-for="(step, i) in steps" :key="i">
        <button @click="currentStep = i"
          :class="['flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all',
            i === currentStep ? 'bg-forge-600 text-white' :
            i < currentStep ? 'bg-forge-600/20 text-forge-400' : 'bg-surface-800 text-surface-500']">
          <span class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold"
            :class="i < currentStep ? 'bg-forge-500 text-white' : 'bg-surface-700'">
            {{ i < currentStep ? '✓' : i + 1 }}
          </span>
          {{ step }}
        </button>
        <div v-if="i < steps.length - 1" class="w-6 h-px bg-surface-700"></div>
      </template>
    </div>

    <!-- Step 1: Basic Info -->
    <div v-show="currentStep === 0" class="glass-card p-6 animate-slide-up">
      <h3 class="section-title mb-5">Basic Information</h3>
      <div class="space-y-4">
        <div>
          <label class="label-text">Scenario Name *</label>
          <input v-model="form.name" class="input-field" placeholder="e.g. Blind Corner Human Crossing" />
        </div>
        <div>
          <label class="label-text">Description</label>
          <textarea v-model="form.description" rows="3" class="input-field" placeholder="Describe the edge case being tested..."></textarea>
        </div>
        <div>
          <label class="label-text">Notes</label>
          <textarea v-model="form.notes" rows="2" class="input-field" placeholder="Internal notes..."></textarea>
        </div>
      </div>
    </div>

    <!-- Step 2: Environment -->
    <div v-show="currentStep === 1" class="glass-card p-6 animate-slide-up">
      <h3 class="section-title mb-5">Environment Setup</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="label-text">Environment Template</label>
          <select v-model="form.environment_template" class="select-field">
            <option value="warehouse_aisle">Warehouse Aisle</option>
            <option value="warehouse_open_floor">Open Floor</option>
            <option value="warehouse_loading_dock">Loading Dock</option>
            <option value="warehouse_cold_storage">Cold Storage</option>
          </select>
        </div>
        <div>
          <label class="label-text">Robot Path Type</label>
          <select v-model="form.robot_path_type" class="select-field">
            <option value="left_turn_blind_corner">Left Turn (Blind Corner)</option>
            <option value="right_turn_blind_corner">Right Turn (Blind Corner)</option>
            <option value="straight_aisle">Straight Aisle</option>
            <option value="t_junction">T-Junction</option>
            <option value="cross_intersection">Cross Intersection</option>
            <option value="u_turn">U-Turn</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Step 3: Hazards -->
    <div v-show="currentStep === 2" class="glass-card p-6 animate-slide-up">
      <h3 class="section-title mb-5">Hazard Configuration</h3>
      <div class="space-y-5">
        <div>
          <label class="label-text">Human Crossing Probability: {{ (form.human_crossing_probability * 100).toFixed(0) }}%</label>
          <input type="range" v-model.number="form.human_crossing_probability" min="0" max="1" step="0.05"
            class="w-full h-2 bg-surface-800 rounded-full appearance-none cursor-pointer accent-forge-500" />
          <div class="flex justify-between text-xs text-surface-500 mt-1"><span>0%</span><span>100%</span></div>
        </div>
        <div>
          <label class="label-text">Dropped Obstacle Level</label>
          <select v-model="form.dropped_obstacle_level" class="select-field">
            <option value="none">None</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="extreme">Extreme</option>
          </select>
        </div>
        <div class="flex items-center gap-3">
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="form.blocked_aisle_enabled" class="sr-only peer" />
            <div class="w-11 h-6 bg-surface-700 rounded-full peer peer-checked:bg-forge-600 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full"></div>
          </label>
          <span class="text-sm text-surface-300">Blocked Aisle Enabled</span>
        </div>
      </div>
    </div>

    <!-- Step 4: Dynamics -->
    <div v-show="currentStep === 3" class="glass-card p-6 animate-slide-up">
      <h3 class="section-title mb-5">Dynamics & Timing</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="label-text">Lighting Preset</label>
          <select v-model="form.lighting_preset" class="select-field">
            <option value="normal">Normal</option>
            <option value="low_light">Low Light</option>
            <option value="high_contrast">High Contrast</option>
            <option value="flickering">Flickering</option>
            <option value="emergency">Emergency</option>
          </select>
        </div>
        <div>
          <label class="label-text">Camera Mode</label>
          <select v-model="form.camera_mode" class="select-field">
            <option value="overhead">Overhead</option>
            <option value="follow">Follow</option>
            <option value="fixed_angle">Fixed Angle</option>
            <option value="first_person">First Person</option>
            <option value="multi_view">Multi-View</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Step 5: Variants -->
    <div v-show="currentStep === 4" class="glass-card p-6 animate-slide-up">
      <h3 class="section-title mb-5">Variant Settings</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="label-text">Variant Count: {{ form.variant_count }}</label>
          <input type="range" v-model.number="form.variant_count" min="1" max="50" step="1"
            class="w-full h-2 bg-surface-800 rounded-full appearance-none cursor-pointer accent-forge-500" />
          <div class="flex justify-between text-xs text-surface-500 mt-1"><span>1</span><span>50</span></div>
        </div>
        <div>
          <label class="label-text">Random Seed</label>
          <input v-model.number="form.random_seed" type="number" class="input-field" />
        </div>
      </div>
    </div>

    <!-- Step 6: Summary -->
    <div v-show="currentStep === 5" class="glass-card p-6 animate-slide-up">
      <h3 class="section-title mb-5">Summary</h3>
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div v-for="[key, val] in summaryItems" :key="key" class="flex justify-between py-2 border-b border-surface-800/30">
          <span class="text-surface-400">{{ key }}</span>
          <span class="text-white font-medium">{{ val }}</span>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <div class="flex items-center justify-between">
      <button @click="currentStep = Math.max(0, currentStep - 1)" :disabled="currentStep === 0" class="btn-secondary" :class="{ 'opacity-50': currentStep === 0 }">
        ← Back
      </button>
      <div class="flex gap-3">
        <button v-if="currentStep < steps.length - 1" @click="currentStep++" class="btn-primary">
          Next →
        </button>
        <button v-else @click="submitScenario" :disabled="saving" class="btn-primary">
          {{ saving ? 'Creating...' : '🚀 Create Scenario' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const router = useRouter()

const steps = ['Basic Info', 'Environment', 'Hazards', 'Dynamics', 'Variants', 'Summary']
const currentStep = ref(0)
const saving = ref(false)

const form = reactive({
  name: '',
  description: '',
  notes: '',
  environment_template: 'warehouse_aisle',
  robot_path_type: 'left_turn_blind_corner',
  human_crossing_probability: 0.5,
  dropped_obstacle_level: 'medium',
  blocked_aisle_enabled: false,
  lighting_preset: 'normal',
  camera_mode: 'overhead',
  variant_count: 5,
  random_seed: 42,
})

const summaryItems = computed(() => [
  ['Name', form.name || '—'],
  ['Environment', form.environment_template],
  ['Path Type', form.robot_path_type],
  ['Human Probability', `${(form.human_crossing_probability * 100).toFixed(0)}%`],
  ['Obstacle Level', form.dropped_obstacle_level],
  ['Blocked Aisle', form.blocked_aisle_enabled ? 'Yes' : 'No'],
  ['Lighting', form.lighting_preset],
  ['Camera', form.camera_mode],
  ['Variants', form.variant_count],
  ['Seed', form.random_seed],
])

const submitScenario = async () => {
  if (!form.name.trim()) {
    currentStep.value = 0
    return
  }
  saving.value = true
  try {
    await api.createScenario({ ...form })
    router.push('/scenarios')
  } catch (e) {
    console.error(e)
  }
  saving.value = false
}
</script>
