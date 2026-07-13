import { createRouter, createWebHashHistory } from "vue-router";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", redirect: "/chat" },
    { path: "/chat", name: "chat", component: () => import("@/views/ChatView.vue") },
    { path: "/history", name: "history", component: () => import("@/views/HistoryView.vue") },
    { path: "/knowledge", name: "knowledge", component: () => import("@/views/KnowledgeView.vue") },
    { path: "/replies", name: "replies", component: () => import("@/views/RepliesView.vue") },
    { path: "/dashboard", name: "dashboard", component: () => import("@/views/DashboardView.vue") },
  ],
});

export default router;
