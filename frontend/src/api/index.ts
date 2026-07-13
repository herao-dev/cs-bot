import axios from "axios";

const http = axios.create({
  baseURL: "/api",
  timeout: 120000,
});

http.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.message || err.message || "Network error";
    return Promise.reject(new Error(msg));
  }
);

export interface FaqPair {
  id: string; question: string; answer: string;
  category: string; created_at: number; updated_at: number;
}

export interface DocInfo { id: string; name: string; }

export interface SessionInfo {
  id: string; title: string; message_count: number;
  created_at: number; updated_at: number;
}

export interface ChatResponse {
  answer: string;
  sources: { doc_id: string; score: number; excerpt: string }[];
  session_id: string; elapsed: number; timestamp: number;
}

export interface ReplyItem {
  id: string; title: string; content: string;
  tag: string; sort: number; created_at: number;
}

export interface StatsOverview {
  total_sessions: number; total_messages: number;
  faq_count: number; doc_count: number;
  thumbs_up: number; thumbs_down: number; today_sessions: number;
}

export const api = {
  // Chat
  sendMessage(question: string, sessionId: string) {
    return http.post<{ ok: boolean } & ChatResponse>("/chat/send", { question, session_id: sessionId });
  },
  getHistory(sessionId: string) {
    return http.get("/chat/history", { params: { session_id: sessionId } });
  },
  clearHistory(sessionId: string) {
    return http.delete("/chat/history", { params: { session_id: sessionId } });
  },
  // Sessions
  listSessions() {
    return http.get<{ ok: boolean; sessions: SessionInfo[] }>("/chat/sessions");
  },
  createSession() { return http.post("/chat/sessions"); },
  renameSession(id: string, title: string) { return http.put(`/chat/sessions/${id}`, { title }); },
  deleteSession(id: string) { return http.delete(`/chat/sessions/${id}`); },
  // Knowledge - Documents
  listDocuments() { return http.get("/knowledge/documents"); },
  uploadDocument(file: File) {
    const fd = new FormData(); fd.append("file", file);
    return http.post("/knowledge/documents/upload", fd, { headers: { "Content-Type": "multipart/form-data" }, timeout: 300000 });
  },
  deleteDocument(docId: string) { return http.delete(`/knowledge/documents/${encodeURIComponent(docId)}`); },
  // Knowledge - FAQ
  listFaq(keyword?: string) { return http.get("/knowledge/faq", { params: keyword ? { keyword } : {} }); },
  addFaq(q: string, a: string, c: string) { return http.post("/knowledge/faq", { question: q, answer: a, category: c }); },
  updateFaq(id: string, q: string, a: string, c: string) { return http.put(`/knowledge/faq/${id}`, { question: q, answer: a, category: c }); },
  deleteFaq(id: string) { return http.delete(`/knowledge/faq/${id}`); },
  batchDeleteFaq(ids: string[]) { return http.post("/knowledge/faq/batch-delete", { ids }); },
  // Stats
  getStats() { return http.get<{ ok: boolean; stats: StatsOverview }>("/stats/overview"); },
  sendFeedback(data: { session_id: string; question: string; answer: string; type: string }) {
    return http.post("/stats/feedback", data);
  },
  // Quick Replies
  listReplies(tag?: string) { return http.get("/replies", { params: tag ? { tag } : {} }); },
  addReply(title: string, content: string, tag: string) { return http.post("/replies", { title, content, tag }); },
  updateReply(id: string, data: Partial<ReplyItem>) { return http.put(`/replies/${id}`, data); },
  deleteReply(id: string) { return http.delete(`/replies/${id}`); },
  batchDeleteReplies(ids: string[]) { return http.post("/replies/batch-delete", { ids }); },
};
