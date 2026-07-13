<script setup lang="ts">
import { ref, onMounted } from "vue";
import { api, type ReplyItem } from "@/api";

const items = ref<ReplyItem[]>([]);
const loading = ref(false);
const showModal = ref(false);
const editing = ref<ReplyItem | null>(null);
const form = ref({ title: "", content: "", tag: "" });
const selectedIds = ref<Set<string>>(new Set());
const tagFilter = ref("");

async function load() {
  loading.value = true;
  try {
    const res = await api.listReplies(tagFilter.value || undefined);
    items.value = res.data.items || [];
  } catch {} finally { loading.value = false; }
}

function openModal(item?: ReplyItem) {
  if (item) {
    editing.value = item;
    form.value = { title: item.title, content: item.content, tag: item.tag };
  } else {
    editing.value = null;
    form.value = { title: "", content: "", tag: "" };
  }
  showModal.value = true;
}

async function save() {
  if (!form.value.title.trim() || !form.value.content.trim()) return;
  if (editing.value) {
    await api.updateReply(editing.value.id, form.value);
  } else {
    await api.addReply(form.value.title, form.value.content, form.value.tag);
  }
  showModal.value = false;
  load();
}

async function remove(id: string) {
  await api.deleteReply(id);
  selectedIds.value.delete(id);
  load();
}

async function batchRemove() {
  if (selectedIds.value.size === 0) return;
  await api.batchDeleteReplies([...selectedIds.value]);
  selectedIds.value.clear();
  load();
}

function toggleSelect(id: string) {
  const s = new Set(selectedIds.value);
  s.has(id) ? s.delete(id) : s.add(id);
  selectedIds.value = s;
}

function toggleAll() {
  selectedIds.value = selectedIds.value.size === items.value.length
    ? new Set()
    : new Set(items.value.map(r => r.id));
}

function insertToChat(item: ReplyItem) {
  navigator.clipboard.writeText(item.content);
}

onMounted(load);
</script>

<template>
  <div class="replies-page">
    <div class="page-header">
      <div>
        <h2>快捷回复</h2>
        <p class="page-desc">预置回复模板，对话时可快速复制使用</p>
      </div>
      <div class="header-actions">
        <select class="form-select" style="width:auto" v-model="tagFilter" @change="load">
          <option value="">全部标签</option>
          <option value="售后">售后</option>
          <option value="产品">产品</option>
          <option value="物流">物流</option>
          <option value="支付">支付</option>
          <option value="问候">问候</option>
        </select>
        <button v-if="selectedIds.size" class="btn btn-sm btn-danger" @click="batchRemove">删除 ({{ selectedIds.size }})</button>
        <button class="btn btn-sm btn-primary" @click="openModal()">添加</button>
      </div>
    </div>

    <div v-if="loading" class="empty-state"><span class="spinner"></span></div>
    <div v-else-if="items.length === 0" class="empty-state"><p>暂无快捷回复</p></div>

    <div v-else class="reply-grid">
      <div v-for="r in items" :key="r.id" class="reply-card">
        <div class="reply-card-header">
          <input type="checkbox" :checked="selectedIds.has(r.id)" @change="toggleSelect(r.id)" />
          <span class="reply-title">{{ r.title }}</span>
          <span v-if="r.tag" class="badge badge-muted">{{ r.tag }}</span>
        </div>
        <div class="reply-content">{{ r.content }}</div>
        <div class="reply-actions">
          <button class="btn btn-xs btn-secondary" @click="insertToChat(r)">复制</button>
          <button class="btn btn-xs btn-secondary" @click="openModal(r)">编辑</button>
          <button class="btn btn-xs btn-danger" @click="remove(r.id)">删除</button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <span>{{ editing ? '编辑' : '添加' }}快捷回复</span>
          <button class="modal-close" @click="showModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group" style="flex:1">
              <label class="form-label">标题</label>
              <input class="form-input" v-model="form.title" placeholder="简明标题" />
            </div>
            <div class="form-group" style="width:120px">
              <label class="form-label">标签</label>
              <select class="form-select" v-model="form.tag">
                <option value="">无</option>
                <option>售后</option><option>产品</option><option>物流</option>
                <option>支付</option><option>问候</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">内容</label>
            <textarea class="form-textarea" v-model="form.content" rows="4" placeholder="回复模板内容"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">取消</button>
          <button class="btn btn-primary" @click="save" :disabled="!form.title.trim() || !form.content.trim()">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.replies-page { flex: 1; overflow: auto; padding: 20px 24px; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 18px; }
.page-header h2 { font-size: 16px; font-weight: 600; }
.page-desc { color: var(--c-text-secondary); font-size: 13px; margin-top: 2px; }
.header-actions { display: flex; gap: 8px; align-items: center; }

.reply-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }

.reply-card {
  background: var(--c-surface); border: 1px solid var(--c-border);
  border-radius: var(--radius); padding: 14px;
}

.reply-card-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
}

.reply-title { font-size: 13px; font-weight: 600; flex: 1; }

.reply-content {
  font-size: 12px; color: var(--c-text-secondary); line-height: 1.6;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  margin-bottom: 10px;
}

.reply-actions { display: flex; gap: 4px; }

.form-row { display: flex; gap: 12px; }
</style>
