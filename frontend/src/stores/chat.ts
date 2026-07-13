import { defineStore } from "pinia";
import { ref } from "vue";
import type { SessionInfo } from "@/api";
import { api } from "@/api";

export const useChatStore = defineStore("chat", () => {
  const sessionId = ref("");
  const messages = ref<(any & { sources?: any[]; ts?: number })[]>([]);
  const sending = ref(false);
  const error = ref("");
  const lastElapsed = ref(0);

  async function ensureSession() {
    if (!sessionId.value) {
      try {
        const res = await api.createSession();
        sessionId.value = res.data.session_id;
      } catch {
        sessionId.value = "default";
      }
    }
  }

  async function send(question: string) {
    await ensureSession();
    sending.value = true;
    error.value = "";

    messages.value.push({ role: "user", content: question });

    try {
      const res = await api.sendMessage(question, sessionId.value);
      const data = res.data;
      lastElapsed.value = data.elapsed || 0;
      messages.value.push({
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        ts: data.timestamp,
      });
    } catch (e: any) {
      error.value = e.message;
      messages.value.push({
        role: "assistant",
        content: "抱歉，服务暂时不可用，请稍后重试。",
      });
    } finally {
      sending.value = false;
    }
  }

  async function loadHistory(sid?: string) {
    const id = sid || sessionId.value;
    if (!id) return;
    sessionId.value = id;
    try {
      const res = await api.getHistory(id);
      messages.value = res.data.messages || [];
    } catch {}
  }

  async function clear() {
    if (sessionId.value) {
      await api.clearHistory(sessionId.value).catch(() => {});
    }
    messages.value = [];
  }

  async function newSession() {
    try {
      const res = await api.createSession();
      sessionId.value = res.data.session_id;
      messages.value = [];
    } catch {}
  }

  function switchSession(id: string) {
    sessionId.value = id;
    messages.value = [];
    loadHistory(id);
  }

  return {
    sessionId,
    messages,
    sending,
    error,
    lastElapsed,
    ensureSession,
    send,
    loadHistory,
    clear,
    newSession,
    switchSession,
  };
});
