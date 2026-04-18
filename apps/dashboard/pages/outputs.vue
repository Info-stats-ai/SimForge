<template>
  <div class="space-y-6">
    <!-- Filters -->
    <div class="flex items-center gap-3">
      <select v-model="typeFilter" class="select-field w-48">
        <option value="">All Types</option>
        <option value="preview_image">Preview Image</option>
        <option value="manifest_json">Manifest</option>
        <option value="labels_json">Labels</option>
        <option value="evaluation_json">Evaluation</option>
        <option value="log_file">Log</option>
      </select>
      <button @click="loadArtifacts" class="btn-secondary text-sm">↻ Refresh</button>
    </div>

    <!-- Artifacts Grid -->
    <div v-if="filtered.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="a in filtered" :key="a.id" class="glass-card-hover p-5 animate-fade-in">
        <!-- Preview -->
        <div class="w-full h-32 rounded-lg bg-surface-800/50 flex items-center justify-center mb-4 overflow-hidden">
          <div class="text-center">
            <span class="text-3xl">{{ artifactIcon(a.artifact_type) }}</span>
            <p class="text-xs text-surface-500 mt-1">{{ a.artifact_type }}</p>
          </div>
        </div>
        <!-- Info -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-medium px-2 py-0.5 rounded bg-surface-800 text-surface-400">
              {{ a.artifact_type }}
            </span>
            <span class="text-xs text-surface-500">{{ formatDate(a.created_at) }}</span>
          </div>
          <p class="text-xs text-surface-500 font-mono truncate">{{ a.file_path }}</p>
          <p class="text-xs text-surface-600">Job: {{ a.job_id.slice(0, 12) }}…</p>
        </div>
      </div>
    </div>
    <EmptyState v-else icon="📦" title="No artifacts" description="Artifacts will appear here after simulation runs complete." />
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const typeFilter = ref('')
const artifacts = ref<any[]>([])

const filtered = computed(() => {
  if (!typeFilter.value) return artifacts.value
  return artifacts.value.filter(a => a.artifact_type === typeFilter.value)
})

const artifactIcon = (type: string) => {
  const map: Record<string, string> = {
    preview_image: '🖼️',
    preview_video: '🎬',
    manifest_json: '📄',
    labels_json: '🏷️',
    evaluation_json: '📊',
    log_file: '📝',
    usd_scene: '🎭',
  }
  return map[type] || '📦'
}

const formatDate = (d: string) => d ? new Date(d).toLocaleDateString() : '—'

const loadArtifacts = async () => {
  try { artifacts.value = await api.getArtifacts() } catch (e) { console.error(e) }
}

onMounted(loadArtifacts)
</script>
