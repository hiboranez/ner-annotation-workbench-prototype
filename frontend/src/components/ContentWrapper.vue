<template>
  <div class="content">
    <router-view/>
  </div>
</template>

<style scoped>
.content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  background-color: #f4f7fc;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}
</style>
