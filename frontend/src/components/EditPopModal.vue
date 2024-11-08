<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center transition-opacity duration-300"
    @click.self="$emit('close')"
  >
    <div
      class="relative bg-white p-6 rounded-lg w-full max-w-md shadow-lg transition-transform duration-300 transform scale-95"
    >
      <button
        @click="$emit('close')"
        class="absolute top-2 right-2 text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-300 rounded-full"
        aria-label="Close"
      >
        &times;
      </button>
      <slot></slot>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
/* Modal animations */
.fixed {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.relative {
  animation: scaleUp 0.3s ease-out;
}

@keyframes scaleUp {
  from {
    transform: scale(0.9);
  }
  to {
    transform: scale(1);
  }
}
</style>
