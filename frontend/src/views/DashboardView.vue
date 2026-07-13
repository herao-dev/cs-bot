<script setup lang="ts">
import { ref, onMounted } from "vue";
import { api, type StatsOverview, type SessionInfo } from "@/api";

const stats = ref<StatsOverview | null>(null);
const recentSessions = ref<SessionInfo[]>([]);
const loading = ref(false);

async function load() {
  loading.value = true;
  try {
    const [sr, sr2] = await Promise.all([
      api.getStats(),
      api.listSessions(),
    ]);
    stats.value = sr.data.stats;
    recentSessions.value = (sr2.data.sessions || []).slice(0, 6);
  } catch {} finally {
    loading.value = false;
  }
}

function pct(a: number, b: number): string {
  if (a + b === 0) return "0%";
  return ((a / (a + b)) * 100).toFixed(0) + "%";
}

onMounted(load);
</script>

<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>仪表盘</h2>
      <button class="btn btn-sm btn-secondary" @click="load">刷新</button>
    </div>

    <div v-if="loading" class="empty-state"><span class="spinner"></span></div>

    <template v-else-if="stats">
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-num">{{ stats.today_sessions }}</div>
          <div class="stat-label">今日会话</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">{{ stats.total_sessions }}</div>
          <div class="stat-label">总会话</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">{{ stats.total_messages }}</div>
          <div class="stat-label">总消息数</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">{{ stats.faq_count }}</div>
          <div class="stat-label">FAQ 条数</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">{{ stats.doc_count }}</div>
          <div class="stat-label">文档数</div>
        </div>
        <div class="stat-card">
          <div class="stat-num">{{ stats.thumbs_up }} / {{ stats.thumbs_down }}</div>
          <div class="stat-label">
            好评率 {{ pct(stats.thumbs_up, stats.thumbs_down) }}
          </div>
        </div>
      </div>

      <div class="section" v-if="recentSessions.length">
        <h3 class="section-title">最近会话</h3>
        <div class="session-list">
          <div v-for="s in recentSessions" :key="s.id" class="session-row">
            <span class="session-name">{{ s.title }}</span>
            <span class="session-msg-count">{{ s.message_count }} 条消息</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dashboard { flex: 1; overflow: auto; padding: 20px 24px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-header h2 { font-size: 16px; font-weight: 600; }

.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 24px; }

.stat-card {
  background: var(--c-surface); border: 1px solid var(--c-border);
  border-radius: var(--radius); padding: 18px 20px;
}

.stat-num { font-size: 24px; font-weight: 700; color: var(--c-text); }
.stat-label { font-size: 12px; color: var(--c-text-secondary); margin-top: 4px; }

.section { margin-top: 6px; }

.section-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; }

.session-list { border: 1px solid var(--c-border); border-radius: var(--radius); overflow: hidden; }

.session-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; background: var(--c-surface);
}

.session-row:not(:last-child) { border-bottom: 1px solid var(--c-border-light); }

.session-name { font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.session-msg-count { font-size: 12px; color: var(--c-text-muted); flex-shrink: 0; margin-left: 12px; }
</style>
