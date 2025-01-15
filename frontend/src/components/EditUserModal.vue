<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content">
      <h3 class="text-xl font-semibold mb-4">Edit User</h3>
      <form @submit.prevent="saveChanges">
        <div class="mb-4">
          <label class="block text-gray-700">First Name</label>
          <input
            v-model="editedUser.first_name"
            class="input-field"
            type="text"
            placeholder="Enter first name"
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700">Last Name</label>
          <input
            v-model="editedUser.last_name"
            class="input-field"
            type="text"
            placeholder="Enter last name"
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700">Email</label>
          <input
            v-model="editedUser.user_email"
            class="input-field"
            type="email"
            placeholder="Enter email"
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700">Role</label>
          <select v-model="editedUser.role" class="input-field">
            <option value="member">Member</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <div class="flex justify-between">
          <button type="submit" class="btn-primary">Save Changes</button>
          <button type="button" @click="deleteUser" class="btn-danger">
            Delete User
          </button>
        </div>
      </form>

      <button @click="close" class="modal-close">Close</button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    visible: Boolean,
    user: Object,
    onClose: Function,
    onUpdate: Function,
    onDelete: Function,
  },
  data() {
    return {
      editedUser: {},
    }
  },
  watch: {
    visible: {
      immediate: true,
      handler(newValue) {
        if (newValue && this.user) {
          // Prefill editedUser when modal becomes visible
          this.editedUser = { ...this.user }
        }
      },
    },
  },
  methods: {
    close() {
      this.onClose()
    },
    async saveChanges() {
      try {
        await this.onUpdate(this.editedUser)
        alert('User updated successfully')
        this.close()
      } catch (error) {
        console.error('Error saving changes:', error)
        alert('Failed to update user.')
      }
    },
    async deleteUser() {
      if (confirm(`Are you sure you want to delete ${this.user.user_email}?`)) {
        try {
          await this.onDelete(this.user)
          alert('User deleted successfully')
          this.close()
        } catch (error) {
          console.error('Error deleting user:', error)
          alert('Failed to delete user.')
        }
      }
    },
  },
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal-content {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.modal-close {
  margin-top: 1rem;
  text-align: center;
  color: gray;
}
</style>
