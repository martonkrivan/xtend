<template>
  <div class="p-4">
    <div class="mb-4">
      <span class="text-sm">Status: {{ socketStatus }}</span>
    </div>

    <div class="mb-4">
      <pre class="bg-gray-100 p-2 rounded text-sm">{{ JSON.stringify(state, null, 2) }}</pre>
    </div>

    <div class="mb-4 space-y-2">
      <div>
        <label class="block text-sm">Total Cycles:</label>
        <input v-model="startParams.total_cycles" type="number" class="border p-1 rounded w-full" />
      </div>
      <div>
        <label class="block text-sm">Actuation Time (minutes):</label>
        <input v-model="startParams.actuation_time" type="number" step="0.1" class="border p-1 rounded w-full" />
      </div>
      <div>
        <label class="block text-sm">Rest Time (minutes):</label>
        <input v-model="startParams.rest_time" type="number" step="0.1" class="border p-1 rounded w-full" />
      </div>
      <div>
        <label class="block text-sm">Current Cutoff:</label>
        <input v-model="startParams.current_cutoff" type="number" step="0.1" class="border p-1 rounded w-full" />
      </div>
    </div>

    <div class="space-x-2">
      <button @click="handleStart(startParams)" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
        Start
      </button>
      <button @click="handleCancel" class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">
        Cancel
      </button>
      <button @click="handleReset" class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
        Reset
      </button>
    </div>
  </div>
</template>

<script setup>
const { state, socketStatus, handleStart, handleCancel, handleReset } = useSocket()

const startParams = ref({
  total_cycles: 1,
  actuation_time: 1,
  rest_time: 1,
  current_cutoff: 1
})
</script>
