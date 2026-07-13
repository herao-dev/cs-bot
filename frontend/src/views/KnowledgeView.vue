<script setup lang="ts">
import { ref, onMounted } from "vue";
import { api, type FaqPair, type DocInfo } from "@/api";

const tab = ref<"faq" | "docs">("faq");

// --- FAQ ---
const faqList = ref<FaqPair[]>([]);
const faqLoading = ref(false);
const faqKeyword = ref("");
const selectedFaqIds = ref<Set<string>>(new Set());

// FAQ modal
const showFaqModal = ref(false);
const editingFaq = ref<FaqPair | null>(null);
const faqForm = ref({ question: "", answer: "", category: "" });

async function loadFaq() {
  faqLoading.value = true;
  try {
    const res = await api.listFaq(faqKeyword.value || undefined);
    faqList.value = res.data.pairs || [];
  } catch {} finally {
    faqLoading.value = false;
  }
}

function openFaqModal(pair?: FaqPair) {
  if (pair) {
    editingFaq.value = pair;
    faqForm.value = { question: pair.question, answer: pair.answer, category: pair.category };
  } else {
    editingFaq.value = null;
    faqForm.value = { question: "", answer: "", category: "" };
  }
  showFaqModal.value = true;
}

async function saveFaq() {
  if (!faqForm.value.question.trim() || !faqForm.value.answer.trim()) return;
  if (editingFaq.value) {
    await api.updateFaq(editingFaq.value.id, faqForm.value.question, faqForm.value.answer, faqForm.value.category);
  } else {
    await api.addFaq(faqForm.value.question, faqForm.value.answer, faqForm.value.category);
  }
  showFaqModal.value = false;
  loadFaq();
}

async function deleteFaq(id: string) {
  await api.deleteFaq(id);
  selectedFaqIds.value.delete(id);
  loadFaq();
}

async function batchDeleteFaq() {
  if (selectedFaqIds.value.size === 0) return;
  await api.batchDeleteFaq([...selectedFaqIds.value]);
  selectedFaqIds.value.clear();
  loadFaq();
}

function toggleFaqSelect(id: string) {
  const s = new Set(selectedFaqIds.value);
  if (s.has(id)) s.delete(id); else s.add(id);
  selectedFaqIds.value = s;
}

function toggleAllFaq() {
  if (selectedFaqIds.value.size === faqList.value.length) {
    selectedFaqIds.value = new Set();
  } else {
    selectedFaqIds.value = new Set(faqList.value.map(p => p.id));
  }
}

// --- Documents ---
const docList = ref<DocInfo[]>([]);
const docLoading = ref(false);
const uploading = ref(false);
const uploadMsg = ref("");

async function loadDocs() {
  docLoading.value = true;
  try {
    const res = await api.listDocuments();
    docList.value = res.data.documents || [];
  } catch {} finally {
    docLoading.value = false;
  }
}

async function handleUpload(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  uploading.value = true;
  uploadMsg.value = "";
  try {
    await api.uploadDocument(file);
    uploadMsg.value = `${file.name} 上传成功`;
    loadDocs();
  } catch (e: any) {
    uploadMsg.value = e.message;
  } finally {
    uploading.value = false;
    target.value = "";
  }
}

async function deleteDoc(id: string) {
  await api.deleteDocument(id);
  loadDocs();
}

onMounted(() => {
  loadFaq();
  loadDocs();
});

function categoryColor(cat: string): string {
  const map: Record<string, string> = { "售后": "#dc3545", "产品": "#2563eb", "物流": "#d97706", "支付": "#16a34a" };
  return map[cat] || "#6b7280";
}
</script>

<template>
  <div class="knowledge-page">
    <div class="page-header">
      <h2>知识库管理</h2>
      <div class="tab-bar">
        <button class="tab-btn" :class="{ active: tab === 'faq' }" @click="tab = 'faq'">FAQ 问答对</button>
        <button class="tab-btn" :class="{ active: tab === 'docs' }" @click="tab = 'docs'">文档知识</button>
      </div>
    </div>

    <!-- FAQ Tab -->
    <div v-if="tab === 'faq'" class="tab-content">
      <div class="toolbar">
        <div class="toolbar-left">
          <input
            class="form-input search-input"
            v-model="faqKeyword"
            placeholder="搜索 FAQ..."
            @keyup.enter="loadFaq"
          />
          <button class="btn btn-sm btn-secondary" @click="loadFaq">搜索</button>
        </div>
        <div class="toolbar-right">
          <button
            v-if="selectedFaqIds.size > 0"
            class="btn btn-sm btn-danger"
            @click="batchDeleteFaq"
          >删除选中 ({{ selectedFaqIds.size }})</button>
          <button class="btn btn-sm btn-primary" @click="openFaqModal()">添加 FAQ</button>
        </div>
      </div>

      <div v-if="faqLoading" class="empty-state"><span class="spinner"></span></div>

      <div v-else-if="faqList.length === 0" class="empty-state">
        <p>暂无 FAQ 条目</p>
      </div>

      <div v-else class="faq-table-wrap">
        <table class="faq-table">
          <thead>
            <tr>
              <th style="width:36px">
                <input type="checkbox" :checked="selectedFaqIds.size === faqList.length && faqList.length > 0" @change="toggleAllFaq" />
              </th>
              <th style="width:30%">问题</th>
              <th style="width:42%">答案</th>
              <th style="width:80px">分类</th>
              <th style="width:120px">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in faqList" :key="p.id">
              <td>
                <input type="checkbox" :checked="selectedFaqIds.has(p.id)" @change="toggleFaqSelect(p.id)" />
              </td>
              <td class="faq-q">{{ p.question }}</td>
              <td class="faq-a">{{ p.answer }}</td>
              <td>
                <span v-if="p.category" class="badge" :style="{ background: categoryColor(p.category) + '1a', color: categoryColor(p.category), border: '1px solid ' + categoryColor(p.category) + '33' }">{{ p.category }}</span>
                <span v-else class="badge badge-muted">-</span>
              </td>
              <td>
                <div class="action-btns">
                  <button class="btn btn-xs btn-secondary" @click="openFaqModal(p)">编辑</button>
                  <button class="btn btn-xs btn-danger" @click="deleteFaq(p.id)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Docs Tab -->
    <div v-if="tab === 'docs'" class="tab-content">
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="hint-text">支持 PDF、Word、Markdown、TXT 文件</span>
        </div>
        <div class="toolbar-right">
          <label class="btn btn-sm btn-primary" :class="{ disabled: uploading }">
            <span v-if="uploading" class="spinner" style="width:14px;height:14px"></span>
            <span v-else>上传文档</span>
            <input type="file" hidden accept=".pdf,.docx,.txt,.md" @change="handleUpload" :disabled="uploading" />
          </label>
        </div>
      </div>

      <div v-if="uploadMsg" class="msg" :class="uploadMsg.includes('成功') ? 'msg-success' : 'msg-error'">
        {{ uploadMsg }}
      </div>

      <div v-if="docLoading" class="empty-state"><span class="spinner"></span></div>

      <div v-else-if="docList.length === 0" class="empty-state">
        <span class="icon">&#128196;</span>
        <p>暂无文档，上传文件后 AI 将自动学习其中内容</p>
      </div>

      <div v-else class="doc-list">
        <div v-for="doc in docList" :key="doc.id" class="doc-item">
          <div class="doc-icon">
            <template v-if="doc.name.endsWith('.pdf')">PDF</template>
            <template v-else-if="doc.name.endsWith('.docx')">DOC</template>
            <template v-else-if="doc.name.endsWith('.md')">MD</template>
            <template v-else>?</template>
          </div>
          <div class="doc-name">{{ doc.name }}</div>
          <button class="btn btn-xs btn-danger" @click="deleteDoc(doc.id)">删除</button>
        </div>
      </div>
    </div>

    <!-- FAQ Modal -->
    <div v-if="showFaqModal" class="modal-overlay" @click.self="showFaqModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <span>{{ editingFaq ? '编辑 FAQ' : '添加 FAQ' }}</span>
          <button class="modal-close" @click="showFaqModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">分类</label>
            <select class="form-select" v-model="faqForm.category">
              <option value="">无分类</option>
              <option value="售后">售后</option>
              <option value="产品">产品</option>
              <option value="物流">物流</option>
              <option value="支付">支付</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">问题</label>
            <input class="form-input" v-model="faqForm.question" placeholder="客户可能会问的问题" />
          </div>
          <div class="form-group">
            <label class="form-label">答案</label>
            <textarea class="form-textarea" v-model="faqForm.answer" rows="5" placeholder="标准回复内容"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showFaqModal = false">取消</button>
          <button class="btn btn-primary" @click="saveFaq" :disabled="!faqForm.question.trim() || !faqForm.answer.trim()">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.knowledge-page {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: var(--c-surface);
  border-bottom: 1px solid var(--c-border);
  flex-shrink: 0;
}

.page-header h2 {
  font-size: 15px;
  font-weight: 600;
}

.tab-bar {
  display: flex;
  gap: 0;
  background: var(--c-bg);
  border-radius: var(--radius);
  padding: 2px;
}

.tab-btn {
  padding: 5px 14px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 500;
  color: var(--c-text-secondary);
  border-radius: var(--radius-sm);
  transition: all 0.1s;
}

.tab-btn.active {
  background: var(--c-surface);
  color: var(--c-text);
  box-shadow: var(--shadow-sm);
}

.tab-content {
  flex: 1;
  overflow: auto;
  padding: 16px 20px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  gap: 8px;
  align-items: center;
  flex: 1;
}

.search-input {
  max-width: 240px;
}

.toolbar-right {
  display: flex;
  gap: 6px;
}

.hint-text {
  font-size: 12px;
  color: var(--c-text-muted);
}

.faq-table-wrap {
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  overflow: hidden;
}

.faq-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.faq-table th,
.faq-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--c-border-light);
}

.faq-table th {
  background: var(--c-bg);
  font-weight: 600;
  font-size: 12px;
  color: var(--c-text-secondary);
}

.faq-table tr:last-child td {
  border-bottom: none;
}

.faq-table tr:hover td {
  background: #fafbfc;
}

.faq-q,
.faq-a {
  max-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-btns {
  display: flex;
  gap: 4px;
}

.doc-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  overflow: hidden;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--c-surface);
}

.doc-item:not(:last-child) {
  border-bottom: 1px solid var(--c-border-light);
}

.doc-icon {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: var(--c-text-secondary);
  flex-shrink: 0;
}

.doc-name {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.form-group {
  margin-bottom: 14px;
}
</style>
