<template>
  <div class="sidebar">
    <router-link to="/import" class="sidebar-link">数据导入</router-link>
    <router-link to="/overview" class="sidebar-link">数据概览</router-link>
    <router-link to="/annotation" class="sidebar-link">数据标注</router-link>
    <router-link to="/export" class="sidebar-link">数据导出</router-link>
  </div>
</template>

<style scoped>
.sidebar {
  width: 240px; /* 适当增加宽度 */
  background: #34495e; /* 深灰蓝色 */
  color: white;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.1);
}

.sidebar-link {
  color: white;
  text-decoration: none;
  font-size: 18px;
  margin-bottom: 15px;
  padding: 10px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.sidebar-link:hover {
  background-color: #2980b9;
}

.sidebar-link.router-link-active {
  font-weight: bold;
  background-color: #1f578d; /* 更深的蓝色背景 */
}
</style>
