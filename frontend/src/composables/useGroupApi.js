import { ref } from 'vue'
import axios from 'axios'

export default function useGroupApi(apiBaseUrl) {
    const groups = ref([])

    const fetchGroups = async () => {
        try {
            const response = await axios.get(`${apiBaseUrl}/groups/`)
            groups.value = response.data
        } catch (error) {
            console.error('Error fetching groups:', error)
        }
    }

    const createGroup = async (name) => {
        try {
            const response = await axios.post(`${apiBaseUrl}/groups/`, { name })
            groups.value.push(response.data)
        } catch (error) {
            console.error('Error creating group:', error)
            alert('Failed to create a new group. Please try again.')
        }
    }

    const updateGroupName = async (groupId, newName) => {
        try {
            const response = await axios.put(`${apiBaseUrl}/groups/${groupId}/rename/`, { name: newName })
            const updatedGroup = response.data
            const index = groups.value.findIndex(group => group.id === groupId)
            if (index !== -1) groups.value[index].name = updatedGroup.name
        } catch (error) {
            console.error('Error renaming group:', error)
            alert('Failed to rename group. Please try again.')
        }
    }

    const updateGroupColor = async (groupId, color) => {
        try {
            const response = await axios.put(`${apiBaseUrl}/groups/${groupId}/`, { color })
            const updatedGroup = response.data
            const index = groups.value.findIndex(group => group.id === groupId)
            if (index !== -1) groups.value[index].color = updatedGroup.color
        } catch (error) {
            console.error('Error updating group color:', error)
            alert('Failed to update group color. Please try again.')
        }
    }

    const deleteGroup = async (groupId) => {
        try {
            await axios.delete(`${apiBaseUrl}/groups/${groupId}/`)
            groups.value = groups.value.filter(group => group.id !== groupId)
        } catch (error) {
            console.error('Error deleting group:', error)
            alert('Failed to delete the group. Please try again.')
        }
    }

    return {
        groups,
        fetchGroups,
        createGroup,
        updateGroupName,
        updateGroupColor,
        deleteGroup
    }
}
