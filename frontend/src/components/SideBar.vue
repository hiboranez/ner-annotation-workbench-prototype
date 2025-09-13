<template>
  <div class="sidebar">
    <router-link to="/import">数据导入</router-link>
    <router-link to="/overview">数据概览</router-link>
    <router-link to="/annotation">数据标注</router-link>
    <router-link to="/export">数据导出</router-link>
  </div>
</template>

<style>
.sidebar {
  width: 200px;
  background: #34495e;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 20px;
}
.sidebar a {
  margin-bottom: 10px;
  color: white;
  text-decoration: none;
}
.sidebar a.router-link-active {
  font-weight: bold;
}
</style>
