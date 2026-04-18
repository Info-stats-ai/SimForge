<template>
  <div class="stat-card animate-fade-in">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-xs font-medium text-surface-500 uppercase tracking-wider">{{ label }}</p>
        <p class="text-2xl font-bold text-white mt-1.5">{{ value }}</p>
        <p v-if="subtitle" class="text-xs text-surface-500 mt-1">{{ subtitle }}</p>
      </div>
      <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', iconBgClass]">
        <slot name="icon">
          <span class="text-lg">{{ icon }}</span>
        </slot>
      </div>
    </div>
    <div v-if="trend !== undefined" class="mt-3 flex items-center gap-1.5">
      <span :class="trend >= 0 ? 'text-success' : 'text-danger'" class="text-xs font-semibold">
        {{ trend >= 0 ? '↑' : '↓' }} {{ Math.abs(trend) }}%
      </span>
      <span class="text-xs text-surface-500">vs last period</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  subtitle?: string
  icon?: string
  iconBgClass?: string
  trend?: number
}>()
</script>
