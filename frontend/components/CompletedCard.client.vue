<template>
    <div
        class="flex-1 flex flex-col justify-between rounded-xl h-full p-4 bg-white/5 backdrop-blur box-shadow-lg text-center">
        <div class="flex flex-col gap-1">
            <UIcon name="i-ph-check-circle-bold" class="text-4xl text-green-500 self-center flex-shrink-0" />
            <h2 class="font-bold text-center">Test Completed</h2>
        </div>

        <div class="flex flex-col items-center py-1 border border-slate-800 rounded-lg">
            <p class="text-xs">Completed</p>
            <p class="text-xl font-bold">{{ (state as any).current_cycle }}/{{ (state as any).total_cycles
            }}</p>
        </div>

        <UButton size="lg" color="info" class="w-full font-bold justify-center cursor-pointer" icon="i-ph-plus-bold"
            @click="handleReset">
            New test
        </UButton>
    </div>
</template>

<script setup lang="ts">
import { useSocket } from '~/composables/useSocket'

const { state, handleReset } = useSocket()
// Results card component
</script>
