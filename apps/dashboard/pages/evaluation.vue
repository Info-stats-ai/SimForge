<template>
  <div class="space-y-6">
    <!-- Score Summary -->
    <div v-if="evaluations.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      <ScoreCard label="Avg Collision Risk" :score="avgScore('collision_risk_score')" description="Likelihood of robot-human collision" />
      <ScoreCard label="Avg Occlusion" :score="avgScore('occlusion_score')" description="Sensor field obstruction level" />
      <ScoreCard label="Avg Path Conflict" :score="avgScore('path_conflict_score')" description="Route intersection intensity" />
      <ScoreCard label="Avg Severity" :score="avgScore('severity_score')" description="Overall edge-case severity" />
      <ScoreCard label="Avg Diversity" :score="avgScore('diversity_score')" description="Scenario variation coverage" />
    </div>

    <!-- Evaluations Table -->
    <div class="glass-card overflow-hidden">
      <div class="p-5 border-b border-surface-800/50">
        <h3 class="section-title">Evaluation Reports</h3>
      </div>
      <div v-if="evaluations.length" class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-surface-800/50">
              <th class="table-header">Job</th>
              <th class="table-header">Collision</th>
              <th class="table-header">Occlusion</th>
              <th class="table-header">Conflict</th>
              <th class="table-header">Severity</th>
              <th class="table-header">Diversity</th>
              <th class="table-header">Risk Factors</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in evaluations" :key="e.id" class="table-row cursor-pointer" @click="selected = e">
              <td class="table-cell font-mono text-xs text-surface-400">{{ e.job_id.slice(0, 12) }}…</td>
              <td class="table-cell"><ScorePill :score="e.collision_risk_score" /></td>
              <td class="table-cell"><ScorePill :score="e.occlusion_score" /></td>
              <td class="table-cell"><ScorePill :score="e.path_conflict_score" /></td>
              <td class="table-cell"><ScorePill :score="e.severity_score" /></td>
              <td class="table-cell"><ScorePill :score="e.diversity_score" /></td>
              <td class="table-cell text-xs text-surface-400">{{ (e.top_risk_factors || []).length }} factors</td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState v-else icon="📊" title="No evaluations" description="Evaluations are generated after simulation runs complete." />
    </div>

    <!-- Detail Panel -->
    <div v-if="selected" class="glass-card p-6 animate-slide-up">
      <div class="flex items-center justify-between mb-4">
        <h3 class="section-title">Evaluation Detail</h3>
        <button @click="selected = null" class="btn-ghost text-sm">✕ Close</button>
      </div>
      <div class="bg-surface-950 rounded-lg p-4 font-mono text-sm text-surface-300 whitespace-pre-line mb-4">{{ selected.explanation }}</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 class="text-sm font-semibold text-surface-300 mb-2">Top Risk Factors</h4>
          <ul class="space-y-1">
            <li v-for="r in (selected.top_risk_factors || [])" :key="r" class="text-sm text-danger/80 flex items-start gap-2">
              <span class="text-danger mt-0.5">⚠</span> {{ r }}
            </li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-semibold text-surface-300 mb-2">Recommended Actions</h4>
          <ul class="space-y-1">
            <li v-for="a in (selected.recommended_actions || [])" :key="a" class="text-sm text-forge-400/80 flex items-start gap-2">
              <span class="text-forge-400 mt-0.5">→</span> {{ a }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const evaluations = ref<any[]>([])
const selected = ref<any>(null)

const avgScore = (key: string) => {
  if (!evaluations.value.length) return 0
  return evaluations.value.reduce((sum, e) => sum + (e[key] || 0), 0) / evaluations.value.length
}

onMounted(async () => {
  try { evaluations.value = await api.getEvaluations() } catch (e) { console.error(e) }
})

// Inline ScorePill component
const ScorePill = defineComponent({
  props: { score: { type: Number, required: true } },
  setup(props) {
    const cls = computed(() => {
      if (props.score < 0.3) return 'bg-success/10 text-success'
      if (props.score < 0.6) return 'bg-warning/10 text-warning'
      if (props.score < 0.8) return 'bg-orange-500/10 text-orange-400'
      return 'bg-danger/10 text-danger'
    })
    return () => h('span', { class: `px-2 py-0.5 rounded text-xs font-semibold ${cls.value}` }, `${(props.score * 100).toFixed(0)}%`)
  }
})
</script>
