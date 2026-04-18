<template>
  <span :class="badgeClass">{{ label || status }}</span>
</template>

<script setup lang="ts">
const props = defineProps<{
  status: string
  label?: string
}>()

const badgeClass = computed(() => {
  const map: Record<string, string> = {
    queued: 'badge-queued',
    preparing: 'badge-preparing',
    running: 'badge-running',
    rendering: 'badge-rendering',
    completed: 'badge-completed',
    failed: 'badge-failed',
    draft: 'badge-draft',
    compiled: 'badge-compiled',
  }
  return map[props.status] || 'badge-draft'
})
</script>
