<template>
  <div class="app-container d-flex flex-column min-vh-100 bg-light">
    <Navbar />
    <main class="flex-grow-1 py-4">
      <router-view />
    </main>
    <footer class="bg-dark text-light text-center py-3 mt-auto border-top border-secondary">
      <div class="container">
        <small>(PPA V2)</small>
      </div>
    </footer>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
</script>

<style>
body {
  font-family: 'Inter', sans-serif;
  background-color: #f8f9fa;
}

.card {
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.08);
}
</style>
