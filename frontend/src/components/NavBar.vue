<template>
  <nav class="navbar">
    <h1>NER-Web</h1>
    <div class="user-actions">
      <span>语言</span>
      <button class="lang-btn">中文</button>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  height: 70px;
  background: #007bff; /* 主色调蓝色 */
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.navbar h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.user-actions {
  display: flex;
  align-items: center;
}

.lang-btn {
  background-color: #fff;
  color: #007bff;
  padding: 5px 10px;
  margin-left: 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.lang-btn:hover {
  background-color: #e3f2fd;
}
</style>
