<template>
  <div class="invitation-manager">
    <h3 class="text-lg font-semibold mb-4">Manage Invitations</h3>
    
    <!-- Add Invitations -->
    <div class="mb-6">
      <textarea
        v-model="emailList"
        placeholder="Enter emails (one per line)"
        class="w-full h-32 p-2 border rounded"
      ></textarea>
      <button @click="addInvitations" class="btn btn-primary mt-2">
        Add Invitations
      </button>
    </div>

    <!-- Invited Users List -->
    <div class="invited-users">
      <h4 class="font-medium mb-2">Invited Users</h4>
      <div v-for="invite in invitedUsers" :key="invite.email" class="flex justify-between items-center p-2 border-b">
        <span>{{ invite.email }}</span>
        <button @click="removeInvitation(invite.id)" class="text-red-500">
          Remove
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// Implementation for managing invitations
</script> 