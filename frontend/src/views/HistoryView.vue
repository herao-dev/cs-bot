<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { api, type SessionInfo } from "@/api";
import { useChatStore } from "@/stores/chat";

const router = useRouter();
const chatStore = useChatStore();
const sessions = ref<SessionInfo[]>([]);
const loading = ref(false);
const selectedIds = ref<Set<string>>(new Set());

async function load() {
  loading.value = true;
  try {
    const res = await api.listSessions();
    sessions.value = res.data.sessions || [];
  } catch {} finally {
    loading.value = false;
  }
}

function openSession(sid: string) {
  chatStore.switchSession(sid);
  router.push({ name: "chat" });
}

async function deleteSession(sid: string) {
  await api.deleteSession(sid);
  selectedIds.value.delete(sid);
  load();
}

async function batchDelete() {
  for (const id of selectedIds.value) {
    await api.deleteSession(id).catch(() => {});
  }
  selectedIds.value.clear();
  load();
}

function toggleSelect(id: string) {
  const s = new Set(selectedIds.value);
  s.has(id) ? s.delete(id) : s.add(id);
  selectedIds.value = s;
}

function toggleAll() {
  if (selectedIds.value.size === sessions.value.length) {
    selectedIds.value = new Set();
  } else {
    selectedIds.value = new Set(sessions.value.map(s => s.id));
  }
}

function formatTime(ts: number): string {
  if (!ts) return "-";
  const d = new Date(ts * 1000);
  const pad = (n: number) => String(n).padStart(2, "0");
  const now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  const time = `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  if (isToday) return `今天 ${time}`;
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${time}`;
}

onMounted(load);
</script>

<template>
  <div class="history-page">
    <div class="page-header">
      <div>
        <h2>对话历史</h2>
        <p class="page-desc">所有会话在服务重启后依然保留</p>
      </div>
      <div class="header-actions">
        <button
          v-if="selectedIds.size > 0"
          class="btn btn-sm btn-danger"
          @click="batchDelete"
        >删除选中 ({{ selectedIds.size }})</button>
        <button class="btn btn-sm btn-secondary" @click="load">刷新</button>
      </div>
    </div>

    <div v-if="loading" class="empty-state"><span class="spinner"></span></div>

    <div v-else-if="sessions.length === 0" class="empty-state">
      <span class="icon">&#128172;</span>
      <p>暂无对话记录</p>
      <button class="btn btn-sm btn-primary" style="margin-top:12px" @click="router.push({name:'chat'})">开始对话</button>
    </div>

    <div v-else class="session-table-wrap">
      <table class="session-table">
        <thead>
          <tr>
            <th style="width:36px">
              <input type="checkbox" :checked="selectedIds.size === sessions.length && sessions.length > 0" @change="toggleAll" />
            </th>
            <th>会话标题</th>
            <th style="width:90px">消息数</th>
            <th style="width:160px">最后更新</th>
            <th style="width:100px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in sessions" :key="s.id" @click="openSession(s.id)" class="clickable">
            <td @click.stop>
              <input type="checkbox" :checked="selectedIds.has(s.id)" @change="toggleSelect(s.id)" />
            </td>
            <td class="session-title">{{ s.title }}</td>
            <td><span class="badge badge-muted">{{ s.message_count }} 条</span></td>
            <td class="session-time">{{ formatTime(s.updated_at) }}</td>
            <td @click.stop>
              <div class="action-btns">
                <button class="btn btn-xs btn-secondary" @click="openSession(s.id)">继续</button>
                <button class="btn btn-xs btn-danger" @click="deleteSession(s.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.history-page {
  flex: 1; overflow: auto; padding: 20px 24px;
}

.page-header {
  display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 16px;
}

.page-header h2 { font-size: 16px; font-weight: 600; }
.page-desc { color: var(--c-text-secondary); font-size: 13px; margin-top: 2px; }
.header-actions { display: flex; gap: 6px; }

.session-table-wrap {
  border: 1px solid var(--c-border); border-radius: var(--radius); overflow: hidden;
}

.session-table {
  width: 100%; border-collapse: collapse; font-size: 13px;
}

.session-table th, .session-table td {
  padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--c-border-light);
}

.session-table th {
  background: var(--c-bg); font-weight: 600; font-size: 12px; color: var(--c-text-secondary);
}

.session-table tr:last-child td { border-bottom: none; }
.session-table tr:hover td { background: #fafbfc; }

.clickable { cursor: pointer; }

.session-title {
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 0; font-weight: 500;
}

.session-time { color: var(--c-text-secondary); font-size: 12px; white-space: nowrap; }
.action-btns { display: flex; gap: 4px; }
</style>
