<template>
  <div class="flex items-center justify-center p-12 text-center animate-fade-in">
    <div>
      <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-surface-800/50 flex items-center justify-center">
        <span class="text-3xl">{{ icon }}</span>
      </div>
      <h3 class="text-lg font-semibold text-surface-300">{{ title }}</h3>
      <p class="text-sm text-surface-500 mt-1 max-w-md">{{ description }}</p>
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon?: string
  title: string
  description: string
}>()
</script>
