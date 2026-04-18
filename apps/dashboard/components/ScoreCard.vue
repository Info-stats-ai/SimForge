<template>
  <div class="glass-card p-5 animate-fade-in">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-semibold text-surface-300">{{ label }}</h3>
      <span class="text-xs font-medium px-2 py-0.5 rounded-full" :class="scoreClass">
        {{ scoreLabel }}
      </span>
    </div>
    <div class="text-3xl font-bold text-white mb-3">{{ (score * 100).toFixed(0) }}%</div>
    <div class="w-full h-2 bg-surface-800 rounded-full overflow-hidden">
      <div class="h-full rounded-full transition-all duration-700 ease-out" :class="barClass" :style="{ width: `${score * 100}%` }"></div>
    </div>
    <p v-if="description" class="text-xs text-surface-500 mt-2">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  label: string
  score: number
  description?: string
}>()

const scoreLabel = computed(() => {
  if (props.score < 0.3) return 'Low'
  if (props.score < 0.6) return 'Moderate'
  if (props.score < 0.8) return 'High'
  return 'Critical'
})

const scoreClass = computed(() => {
  if (props.score < 0.3) return 'bg-success/10 text-success'
  if (props.score < 0.6) return 'bg-warning/10 text-warning'
  if (props.score < 0.8) return 'bg-orange-500/10 text-orange-400'
  return 'bg-danger/10 text-danger'
})

const barClass = computed(() => {
  if (props.score < 0.3) return 'bg-success'
  if (props.score < 0.6) return 'bg-warning'
  if (props.score < 0.8) return 'bg-orange-500'
  return 'bg-danger'
})
</script>
