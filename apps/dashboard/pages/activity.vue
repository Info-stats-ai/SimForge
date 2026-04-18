<template>
  <div class="space-y-6">
    <div class="glass-card overflow-hidden">
      <div class="p-5 border-b border-surface-800/50 flex items-center justify-between">
        <h3 class="section-title">Event Timeline</h3>
        <button @click="loadActivity" class="btn-secondary text-sm">↻ Refresh</button>
      </div>
      <div v-if="activity.length" class="divide-y divide-surface-800/30">
        <div v-for="log in activity" :key="log.id"
          class="flex items-start gap-4 p-4 hover:bg-surface-800/20 transition-colors animate-fade-in">
          <div class="relative">
            <div class="w-10 h-10 rounded-full flex items-center justify-center" :class="iconClass(log.event_type)">
              <span class="text-base">{{ icon(log.event_type) }}</span>
            </div>
            <div class="absolute top-10 left-1/2 -translate-x-1/2 w-px h-full bg-surface-800/50"></div>
          </div>
          <div class="flex-1 pb-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-medium px-2 py-0.5 rounded-full" :class="typeClass(log.event_type)">
                {{ log.event_type.replace(/_/g, ' ') }}
              </span>
              <span class="text-xs text-surface-500">{{ formatTime(log.created_at) }}</span>
            </div>
            <p class="text-sm text-surface-200 mt-1.5">{{ log.message }}</p>
            <p v-if="log.related_entity_id" class="text-xs text-surface-500 font-mono mt-1">
              {{ log.related_entity_type }}: {{ log.related_entity_id.slice(0, 16) }}…
            </p>
          </div>
        </div>
      </div>
      <EmptyState v-else icon="📭" title="No activity" description="System events will appear here." />
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const activity = ref<any[]>([])

const icon = (type: string) => {
  const map: Record<string, string> = {
    scenario_created: '📋', scenario_compiled: '⚙️', run_submitted: '🚀',
    job_completed: '✅', job_failed: '❌', job_started: '▶️',
    job_retried: '🔄', system_info: 'ℹ️',
  }
  return map[type] || '📌'
}

const iconClass = (type: string) => {
  if (type.includes('fail')) return 'bg-danger/10'
  if (type.includes('completed')) return 'bg-success/10'
  if (type.includes('submitted') || type.includes('started')) return 'bg-forge-600/10'
  if (type.includes('compiled')) return 'bg-warning/10'
  return 'bg-surface-800/50'
}

const typeClass = (type: string) => {
  if (type.includes('fail')) return 'bg-danger/10 text-danger'
  if (type.includes('completed')) return 'bg-success/10 text-success'
  if (type.includes('submitted')) return 'bg-forge-600/10 text-forge-400'
  return 'bg-surface-800 text-surface-400'
}

const formatTime = (d: string) => {
  if (!d) return '—'
  return new Date(d).toLocaleString()
}

const loadActivity = async () => {
  try { activity.value = await api.getActivity(50) } catch (e) { console.error(e) }
}

onMounted(loadActivity)
</script>
