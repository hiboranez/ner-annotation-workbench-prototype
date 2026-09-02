<!-- vue -->
<template>
  <div class="auth-page">
    <h2>注册</h2>
    <form @submit.prevent="onSubmit">
      <label>用户名</label>
      <input v-model="username" required/>
      <label>密码</label>
      <input type="password" v-model="password" required/>
      <label>角色</label>
      <select v-model="role">
        <option value="viewer">Viewer（只读）</option>
        <option value="annotator">Annotator（可上传）</option>
      </select>
      <button :disabled="loading">{{ loading ? '处理中...' : '注册' }}</button>
      <p class="err" v-if="err">{{ err }}</p>
    </form>
    <p>已有账号？
      <router-link to="/login">去登录</router-link>
    </p>
  </div>
</template>

<script setup>
import {ref} from 'vue';
import {useRouter} from 'vue-router';
import {useAuthStore} from '@/stores/authStore';

const router = useRouter();
const auth = useAuthStore();

const username = ref('');
const password = ref('');
const role = ref('viewer');
const loading = ref(false);
const err = ref('');

async function onSubmit() {
  err.value = '';
  loading.value = true;
  try {
    await auth.register(username.value, password.value, role.value);
    router.replace('/import');
  } catch (e) {
    err.value = e?.message || '注册失败';
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

input, select {
  width: 100%;
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

button {
  margin-top: 14px;
  width: 100%;
  padding: 10px;
  background: #10b981;
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
