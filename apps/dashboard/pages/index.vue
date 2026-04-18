<template>
  <div class="space-y-8">
    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard label="Total Scenarios" :value="stats.scenarios" icon="📋" iconBgClass="bg-forge-600/10" />
      <StatCard label="Total Runs" :value="stats.totalJobs" icon="🚀" iconBgClass="bg-info/10" />
      <StatCard label="Completed" :value="stats.completedJobs" icon="✅" iconBgClass="bg-success/10" />
      <StatCard label="Failed" :value="stats.failedJobs" icon="❌" iconBgClass="bg-danger/10" />
    </div>

    <!-- Two Column Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Recent Activity -->
      <div class="lg:col-span-2 glass-card p-6">
        <h3 class="section-title mb-4">Recent Activity</h3>
        <div v-if="activity.length" class="space-y-3">
          <div v-for="log in activity.slice(0, 8)" :key="log.id"
            class="flex items-start gap-3 p-3 rounded-lg hover:bg-surface-800/30 transition-colors">
            <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0" :class="activityIconClass(log.event_type)">
              <span class="text-sm">{{ activityIcon(log.event_type) }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-surface-200">{{ log.message }}</p>
              <p class="text-xs text-surface-500 mt-0.5">{{ formatTime(log.created_at) }}</p>
            </div>
          </div>
        </div>
        <EmptyState v-else icon="📭" title="No activity yet" description="Activity will appear here as you create scenarios and run simulations." />
      </div>

      <!-- Quick Stats -->
      <div class="space-y-4">
        <!-- Status Breakdown -->
        <div class="glass-card p-5">
          <h3 class="text-sm font-semibold text-surface-300 mb-4">Job Status Distribution</h3>
          <div class="space-y-3">
            <div v-for="(count, status) in statusCounts" :key="status" class="flex items-center gap-3">
              <StatusBadge :status="String(status)" />
              <div class="flex-1 h-1.5 bg-surface-800 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all duration-500" :class="statusBarClass(String(status))"
                  :style="{ width: `${(count / Math.max(stats.totalJobs, 1)) * 100}%` }"></div>
              </div>
              <span class="text-xs text-surface-400 font-mono w-6 text-right">{{ count }}</span>
            </div>
          </div>
        </div>

        <!-- Platform Info -->
        <div class="glass-card p-5">
          <h3 class="text-sm font-semibold text-surface-300 mb-3">Platform</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-surface-500">Provider</span>
              <span class="text-forge-400 font-medium">Mock</span>
            </div>
            <div class="flex justify-between">
              <span class="text-surface-500">SDK Version</span>
              <span class="text-surface-300 font-mono">0.1.0</span>
            </div>
            <div class="flex justify-between">
              <span class="text-surface-500">API Version</span>
              <span class="text-surface-300 font-mono">0.1.0</span>
            </div>
            <div class="flex justify-between">
              <span class="text-surface-500">Database</span>
              <span class="text-success font-medium">Connected</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Scenarios -->
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="section-title">Recent Scenarios</h3>
        <NuxtLink to="/scenarios" class="btn-ghost text-sm">View All →</NuxtLink>
      </div>
      <div v-if="scenarios.length" class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-surface-800/50">
              <th class="table-header">Name</th>
              <th class="table-header">Template</th>
              <th class="table-header">Variants</th>
              <th class="table-header">Status</th>
              <th class="table-header">Created</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in scenarios.slice(0, 5)" :key="s.id" class="table-row cursor-pointer" @click="navigateTo(`/scenarios`)">
              <td class="table-cell font-medium text-white">{{ s.name }}</td>
              <td class="table-cell"><span class="font-mono text-xs text-surface-400">{{ s.environment_template }}</span></td>
              <td class="table-cell">{{ s.variant_count }}</td>
              <td class="table-cell"><StatusBadge :status="s.status" /></td>
              <td class="table-cell text-surface-500">{{ formatDate(s.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState v-else icon="📋" title="No scenarios" description="Create your first scenario to get started." />
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()

const scenarios = ref<any[]>([])
const jobs = ref<any[]>([])
const activity = ref<any[]>([])

const stats = computed(() => {
  const completed = jobs.value.filter(j => j.status === 'completed').length
  const failed = jobs.value.filter(j => j.status === 'failed').length
  return {
    scenarios: scenarios.value.length,
    totalJobs: jobs.value.length,
    completedJobs: completed,
    failedJobs: failed,
  }
})

const statusCounts = computed(() => {
  const counts: Record<string, number> = {}
  for (const j of jobs.value) {
    counts[j.status] = (counts[j.status] || 0) + 1
  }
  return counts
})

const statusBarClass = (status: string) => {
  const map: Record<string, string> = {
    queued: 'bg-info',
    preparing: 'bg-warning',
    running: 'bg-forge-500',
    rendering: 'bg-purple-500',
    completed: 'bg-success',
    failed: 'bg-danger',
  }
  return map[status] || 'bg-surface-600'
}

const activityIcon = (type: string) => {
  const map: Record<string, string> = {
    scenario_created: '📋',
    scenario_compiled: '⚙️',
    run_submitted: '🚀',
    job_completed: '✅',
    job_failed: '❌',
    job_started: '▶️',
    job_retried: '🔄',
    system_info: 'ℹ️',
  }
  return map[type] || '📌'
}

const activityIconClass = (type: string) => {
  if (type.includes('failed')) return 'bg-danger/10'
  if (type.includes('completed')) return 'bg-success/10'
  if (type.includes('submitted') || type.includes('started')) return 'bg-forge-600/10'
  return 'bg-surface-800/50'
}

const formatDate = (d: string) => d ? new Date(d).toLocaleDateString() : '—'
const formatTime = (d: string) => {
  if (!d) return '—'
  const date = new Date(d)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  return date.toLocaleDateString()
}

onMounted(async () => {
  try {
    const [s, j, a] = await Promise.all([
      api.getScenarios(),
      api.getJobs(),
      api.getActivity(20),
    ])
    scenarios.value = s
    jobs.value = j
    activity.value = a
  } catch (e) {
    console.error('Failed to load dashboard data:', e)
  }
})
</script>
