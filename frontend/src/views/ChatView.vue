<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from "vue";
import { useChatStore } from "@/stores/chat";
import { api, type SessionInfo } from "@/api";

const store = useChatStore();
const input = ref("");
const chatBody = ref<HTMLElement | null>(null);
const showSessionPanel = ref(false);
const sessions = ref<SessionInfo[]>([]);
const feedbackGiven = ref<Set<number>>(new Set());

function scrollToBottom() {
  nextTick(() => {
    if (chatBody.value) {
      chatBody.value.scrollTop = chatBody.value.scrollHeight;
    }
  });
}

async function handleSend() {
  const text = input.value.trim();
  if (!text || store.sending) return;
  input.value = "";
  await store.send(text);
  scrollToBottom();
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}

async function loadSessions() {
  try {
    const res = await api.listSessions();
    sessions.value = res.data.sessions || [];
  } catch {}
}

function selectSession(sid: string) {
  store.switchSession(sid);
  showSessionPanel.value = false;
}

async function handleNewSession() {
  await store.newSession();
  showSessionPanel.value = false;
}

async function handleClearSession() {
  const sid = store.sessionId;
  await store.clear();
  await api.deleteSession(sid).catch(() => {});
  store.sessionId = "";
}

function formatElapsed(s: number): string {
  if (!s) return "";
  if (s < 1) return `${Math.round(s * 1000)}ms`;
  return `${s.toFixed(1)}s`;
}

function sendFeedback(msgIndex: number, type: string) {
  const msg = store.messages[msgIndex];
  if (!msg || msg.role !== "assistant") return;
  const prev = store.messages[msgIndex - 1];
  const question = prev && prev.role === "user" ? prev.content : "";
  feedbackGiven.value.add(msgIndex);
  api.sendFeedback({
    session_id: store.sessionId,
    question,
    answer: msg.content,
    type,
  }).catch(() => {});
}

onMounted(async () => {
  await store.ensureSession();
  store.loadHistory();
  scrollToBottom();
  loadSessions();
});

watch(() => store.messages.length, scrollToBottom);
</script>

<template>
  <div class="chat-layout">
    <div class="chat-header">
      <div class="chat-header-left">
        <button class="btn btn-sm btn-secondary" @click="showSessionPanel = !showSessionPanel">
          &#9776; 会话
        </button>
        <span class="session-label" v-if="store.sessionId">{{ store.sessionId }}</span>
      </div>
      <div class="chat-header-right">
        <span v-if="store.lastElapsed" class="elapsed-badge">{{ formatElapsed(store.lastElapsed) }}</span>
        <button class="btn btn-sm btn-secondary" @click="handleNewSession">新建</button>
        <button class="btn btn-sm btn-secondary" @click="handleClearSession" v-if="store.messages.length">清空</button>
      </div>
    </div>

    <!-- Session Panel -->
    <div v-if="showSessionPanel" class="session-overlay" @click.self="showSessionPanel = false">
      <div class="session-panel">
        <div class="session-panel-header">
          <span>历史会话</span>
          <button class="modal-close" @click="showSessionPanel = false">&times;</button>
        </div>
        <div class="session-list">
          <div v-if="sessions.length === 0" class="empty-state" style="padding:20px"><p>暂无历史会话</p></div>
          <div
            v-for="s in sessions"
            :key="s.id"
            class="session-row"
            :class="{ current: s.id === store.sessionId }"
            @click="selectSession(s.id)"
          >
            <div class="session-row-title">{{ s.title }}</div>
            <div class="session-row-meta">{{ s.message_count }} 条消息</div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-body" ref="chatBody">
      <div v-if="store.messages.length === 0" class="chat-welcome">
        <div class="welcome-icon">?</div>
        <h3>有什么可以帮助你的？</h3>
        <p>基于知识库内容智能回答，支持多轮对话</p>
        <div class="suggestions">
          <button
            v-for="q in ['如何退货？', '退款多久到账？', '如何联系客服？']"
            :key="q"
            class="suggest-btn"
            @click="input = q; handleSend()"
          >{{ q }}</button>
        </div>
      </div>

      <template v-for="(msg, i) in store.messages" :key="i">
        <div class="msg-row" :class="msg.role">
          <div class="msg-avatar">
            <template v-if="msg.role === 'user'">U</template>
            <template v-else>CS</template>
          </div>
          <div class="msg-bubble">
            <div class="msg-text">{{ msg.content }}</div>
            <div v-if="msg.role === 'assistant'" class="msg-feedback">
              <button
                class="feedback-btn"
                :class="{ active: feedbackGiven.has(i) }"
                title="有用"
                @click="sendFeedback(i, 'up')"
                :disabled="feedbackGiven.has(i)"
              >&#128077;</button>
              <button
                class="feedback-btn"
                title="无用"
                @click="sendFeedback(i, 'down')"
                :disabled="feedbackGiven.has(i)"
              >&#128078;</button>
            </div>
            <div v-if="msg.sources && msg.sources.length > 0" class="msg-sources">
              <details>
                <summary>参考来源 ({{ msg.sources.length }})</summary>
                <div v-for="(s, si) in msg.sources" :key="si" class="source-item">
                  <span class="source-label">{{ s.doc_id }}</span>
                  <span class="source-excerpt">{{ s.excerpt }}</span>
                </div>
              </details>
            </div>
          </div>
        </div>
      </template>

      <div v-if="store.sending" class="msg-row assistant">
        <div class="msg-avatar">CS</div>
        <div class="msg-bubble typing">
          <span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>
        </div>
      </div>
    </div>

    <div class="chat-footer">
      <div class="chat-input-wrap">
        <textarea
          class="chat-input"
          v-model="input"
          placeholder="输入问题，Enter 发送，Shift+Enter 换行"
          rows="1"
          @keydown="handleKeydown"
          :disabled="store.sending"
        ></textarea>
      </div>
      <button class="btn btn-primary" :disabled="store.sending || !input.trim()" @click="handleSend">
        发送
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-layout { display: flex; flex-direction: column; height: 100%; }

.chat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 16px; background: var(--c-surface);
  border-bottom: 1px solid var(--c-border); flex-shrink: 0;
}

.chat-header-left { display: flex; align-items: center; gap: 10px; }
.chat-header-right { display: flex; gap: 6px; align-items: center; }

.session-label {
  font-size: 11px; color: var(--c-text-muted); font-family: monospace;
  background: var(--c-bg); padding: 2px 8px; border-radius: 10px;
}

.elapsed-badge {
  font-size: 11px; color: var(--c-text-muted); font-family: monospace;
}

/* Session Panel */
.session-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.3);
  z-index: 100; display: flex; justify-content: flex-start;
}

.session-panel {
  width: 300px; background: var(--c-surface); border-right: 1px solid var(--c-border);
  display: flex; flex-direction: column; box-shadow: 4px 0 16px rgba(0,0,0,0.1);
}

.session-panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; border-bottom: 1px solid var(--c-border-light);
  font-weight: 600; font-size: 14px;
}

.session-list { flex: 1; overflow: auto; }

.session-row {
  padding: 12px 16px; cursor: pointer; border-bottom: 1px solid var(--c-border-light);
  transition: background 0.1s;
}

.session-row:hover { background: var(--c-bg); }
.session-row.current { background: var(--c-accent-light); border-left: 3px solid var(--c-accent); }

.session-row-title { font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.session-row-meta { font-size: 11px; color: var(--c-text-muted); margin-top: 2px; }

/* Chat */
.chat-body {
  flex: 1; overflow-y: auto; padding: 20px;
  display: flex; flex-direction: column; gap: 16px; position: relative;
}

.chat-layout { position: relative; }

.chat-welcome { margin: auto; text-align: center; max-width: 400px; }

.welcome-icon {
  width: 48px; height: 48px; border-radius: 50%;
  background: var(--c-bg); border: 2px solid var(--c-border);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 600; color: var(--c-text-muted);
  margin: 0 auto 14px;
}

.chat-welcome h3 { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
.chat-welcome p { color: var(--c-text-secondary); font-size: 13px; margin-bottom: 14px; }

.suggestions { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }

.suggest-btn {
  padding: 6px 14px; border: 1px solid var(--c-border); border-radius: 14px;
  background: var(--c-surface); font-size: 13px; color: var(--c-text-secondary);
  transition: all 0.1s;
}

.suggest-btn:hover { border-color: var(--c-accent); color: var(--c-accent); background: var(--c-accent-light); }

.msg-row { display: flex; gap: 10px; max-width: 82%; }
.msg-row.user { align-self: flex-end; flex-direction: row-reverse; }

.msg-avatar {
  width: 30px; height: 30px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; flex-shrink: 0;
}

.msg-row.user .msg-avatar { background: var(--c-accent-light); color: var(--c-accent); }
.msg-row.assistant .msg-avatar { background: #f0fdf4; color: var(--c-success); }

.msg-bubble {
  padding: 10px 14px; border-radius: 8px; font-size: 13px; line-height: 1.6;
}

.msg-row.user .msg-bubble { background: var(--c-accent); color: #fff; border-bottom-right-radius: 2px; }
.msg-row.assistant .msg-bubble { background: var(--c-surface); border: 1px solid var(--c-border); border-bottom-left-radius: 2px; }

.msg-bubble.typing { display: flex; gap: 4px; padding: 12px 16px; }

.typing-dot {
  width: 7px; height: 7px; border-radius: 50%; background: var(--c-text-muted);
  animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%,80%,100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.msg-sources { margin-top: 8px; font-size: 12px; }
.msg-sources summary { color: var(--c-text-muted); cursor: pointer; }

.source-item {
  display: flex; flex-direction: column; gap: 2px; margin-top: 4px;
  padding: 6px 8px; background: var(--c-bg); border-radius: var(--radius-sm);
}

.source-label { font-weight: 500; font-size: 11px; color: var(--c-text-secondary); }
.source-excerpt { font-size: 11px; color: var(--c-text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.msg-feedback { display: flex; gap: 4px; margin-top: 6px; }

.feedback-btn {
  background: none; border: 1px solid var(--c-border-light); border-radius: var(--radius-sm);
  padding: 2px 6px; font-size: 12px; cursor: pointer; opacity: 0.6; transition: opacity 0.1s;
}

.feedback-btn:hover:not(:disabled) { opacity: 1; border-color: var(--c-border); }
.feedback-btn.active { opacity: 1; border-color: var(--c-accent); background: var(--c-accent-light); }
.feedback-btn:disabled { cursor: default; }

.chat-footer {
  display: flex; gap: 10px; padding: 12px 16px;
  background: var(--c-surface); border-top: 1px solid var(--c-border); flex-shrink: 0;
}

.chat-input-wrap { flex: 1; }

.chat-input {
  width: 100%; padding: 9px 12px; border: 1px solid var(--c-border);
  border-radius: var(--radius); font-size: 14px; line-height: 1.5;
  resize: none; outline: none; font-family: inherit;
}

.chat-input:focus { border-color: var(--c-accent); box-shadow: 0 0 0 2px var(--c-accent-light); }
.chat-input::placeholder { color: var(--c-text-muted); }
</style>
