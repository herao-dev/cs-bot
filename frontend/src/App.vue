<script setup lang="ts">
import { useRoute } from "vue-router";
const route = useRoute();
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-dot"></span>
        <span>CS Bot</span>
      </div>
      <nav class="sidebar-nav">
        <a class="nav-item" :class="{ active: route.name === 'dashboard' }" href="#/dashboard">
          <svg class="nav-icon" viewBox="0 0 16 16" fill="currentColor"><rect x="1" y="1" width="6" height="6" rx="1"/><rect x="9" y="1" width="6" height="4" rx="1"/><rect x="1" y="9" width="4" height="6" rx="1"/><rect x="7" y="7" width="8" height="8" rx="1"/></svg>
          <span>仪表盘</span>
        </a>
        <a class="nav-item" :class="{ active: route.name === 'chat' }" href="#/chat">
          <svg class="nav-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M2 3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H5l-3 3V3z"/></svg>
          <span>对话</span>
        </a>
        <a class="nav-item" :class="{ active: route.name === 'history' }" href="#/history">
          <svg class="nav-icon" viewBox="0 0 16 16" fill="currentColor"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><polyline points="8,4 8,8 11,10" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
          <span>历史</span>
        </a>
        <a class="nav-item" :class="{ active: route.name === 'replies' }" href="#/replies">
          <svg class="nav-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M2 2h12v3H2V2zm0 4h8v1H2V6zm0 2h10v1H2V8zm0 2h9v1H2v-1zm0 2h12v1H2v-1z"/></svg>
          <span>快捷回复</span>
        </a>
        <a class="nav-item" :class="{ active: route.name === 'knowledge' }" href="#/knowledge">
          <svg class="nav-icon" viewBox="0 0 16 16" fill="currentColor"><path d="M2 2h4v4H2V2zm0 6h4v4H2V8zm6-6h6v4H8V2zm0 6h6v4H8V8z"/></svg>
          <span>知识库</span>
        </a>
      </nav>
      <div class="sidebar-footer"><span>v1.2</span></div>
    </aside>
    <main class="main-content"><router-view /></main>
  </div>
</template>

<style scoped>
.app-shell { display: flex; height: 100%; }
.sidebar {
  width: 180px; min-width: 180px;
  background: var(--c-sidebar); color: var(--c-sidebar-text);
  display: flex; flex-direction: column; user-select: none;
}
.sidebar-brand {
  display: flex; align-items: center; gap: 9px;
  padding: 16px 16px 14px; font-size: 14px; font-weight: 600; color: #e5e7eb;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.brand-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--c-success); }
.sidebar-nav { flex: 1; padding: 10px 8px; display: flex; flex-direction: column; gap: 1px; }
.nav-item {
  display: flex; align-items: center; gap: 9px; padding: 8px 12px;
  border-radius: var(--radius-sm); color: var(--c-sidebar-text);
  text-decoration: none; font-size: 13px; transition: background 0.1s;
}
.nav-item:hover { background: rgba(255,255,255,0.06); }
.nav-item.active { background: var(--c-sidebar-active); color: #e5e7eb; }
.nav-icon { width: 14px; height: 14px; flex-shrink: 0; opacity: 0.7; }
.nav-item.active .nav-icon { opacity: 1; }
.sidebar-footer { padding: 12px 16px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 11px; color: var(--c-text-muted); }
.main-content { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
</style>
