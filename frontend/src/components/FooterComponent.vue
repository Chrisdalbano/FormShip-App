<template>
  <footer class="bg-gray-100 border-t mt-auto">
    <div class="max-w-7xl mx-auto px-4 py-6">
      <div class="flex justify-between items-center">
        <div class="text-sm text-gray-600">
          © {{ new Date().getFullYear() }} FormShip. All rights reserved.
        </div>
        <div class="flex items-center space-x-6">
          <router-link 
            to="/participant/login" 
            class="text-sm text-gray-600 hover:text-blue-600"
          >
            Participant Login
          </router-link>
          <a 
            href="https://formship.com/help" 
            class="text-sm text-gray-600 hover:text-blue-600"
          >
            Help Center
          </a>
        </div>
      </div>
    </div>
  </footer>
</template> 