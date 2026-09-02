<!-- vue -->
<template>
  <div>
    <header class="topbar">
      <div class="brand">数据平台</div>
      <nav class="nav">
        <router-link to="/import">导入</router-link>
        <router-link to="/overview">概览</router-link>
        <router-link to="/annotation">标注</router-link>
        <router-link to="/export">导出</router-link>
      </nav>
      <div class="auth">
        <template v-if="auth.isAuthenticated">
          <span class="who">{{ auth.user?.username }}</span>
          <button @click="logout">退出</button>
        </template>
        <template v-else>
          <router-link to="/login">登录</router-link>
          <router-link to="/register">注册</router-link>
        </template>
      </div>
    </header>
    <main class="main">
      <router-view/>
    </main>
  </div>
</template>

<script setup>
import {useAuthStore} from '@/stores/authStore';

const auth = useAuthStore();
auth.load();

function logout() {
  auth.logout();
}
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 30px;
  padding: 10px 16px;
  background: #1489fb;
  color: #fff;
}

.brand {
  font-weight: 800;
}

.nav {
  display: flex;
  gap: 12px;
}

.nav a {
  color: #cbd5e1;
  text-decoration: none;
}

.nav a.router-link-active {
  color: #fff;
}

.auth {
  display: flex;
  align-items: center;
  gap: 10px;
}

.auth .who {
  color: #a7f3d0;
}

.auth button {
  background: #ef4444;
  border: none;
  color: #fff;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}

.main {
  padding: 16px;
}
</style>
