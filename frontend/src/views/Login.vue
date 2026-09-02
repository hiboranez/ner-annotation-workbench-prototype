<!-- vue -->
<template>
  <div class="auth-page">
    <h2>登录</h2>
    <form @submit.prevent="onSubmit">
      <label>用户名</label>
      <input v-model="username" required/>
      <label>密码</label>
      <input type="password" v-model="password" required/>
      <button :disabled="loading">{{ loading ? '处理中...' : '登录' }}</button>
      <p class="err" v-if="err">{{ err }}</p>
    </form>
    <p>没有账号？
      <router-link to="/register">去注册</router-link>
    </p>
  </div>
</template>

<script setup>
import {ref} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {useAuthStore} from '@/stores/authStore';

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const username = ref('');
const password = ref('');
const loading = ref(false);
const err = ref('');

async function onSubmit() {
  err.value = '';
  loading.value = true;
  try {
    await auth.login(username.value, password.value);
    const redirect = route.query.redirect || '/import';
    router.replace(String(redirect));
  } catch (e) {
    err.value = e?.message || '登录失败';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  max-width: 360px;
  margin: 60px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, .06);
}

label {
  display: block;
  margin: 10px 0 6px;
  color: #374151;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

button {
  margin-top: 14px;
  width: 100%;
  padding: 10px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.err {
  margin-top: 10px;
  color: #dc2626;
}
</style>
