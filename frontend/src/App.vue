<template>
  <div id="app">
    <Navbar/>
    <div class="layout">
      <Sidebar/>
      <ContentWrapper/>
    </div>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'
import Sidebar from './components/Sidebar.vue'
import ContentWrapper from './components/ContentWrapper.vue'

export default {
  components: {Navbar, Sidebar, ContentWrapper}
}
</script>

<style>
.layout {
  display: flex;
  height: 100vh;
}
</style>
