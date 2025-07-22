<template>
    <div
        class="flex-1 flex flex-col justify-between rounded-xl h-full p-4 bg-white/5 backdrop-blur box-shadow-lg text-center">

        <div class="flex justify-start items-center gap-2 -mt-2 -mr-4">
            <label class="text-xs font-bold uppercase tracking-wider flex-shrink-0">Autopilot</label>
            <USeparator class="w-full" />
        </div>
        <UProgress color="info" />
        <h2 class="font-bold text-center">Testing in Progress</h2>

        <!-- <div class="flex flex-col text-center gap-1 p-2 rounded-lg border border-slate-700">
            <span class="text-xl font-bold h-5">{{ (state as any).current_cycle }}/{{ (state as any).total_cycles
                }}</span>
            <p class="text-sm">
                cycles completed
            </p>
        </div>

        <div class="flex-1 text-center flex flex-col gap-1 p-2 rounded-lg border border-slate-700">
            <span class="text-xl font-bold h-5">{{ (state as any).phase }}</span>
            <p class="text-sm">
                phase
            </p>
        </div>
        <div class="flex-1 text-center flex flex-col gap-1 p-2 rounded-lg border border-slate-700">
            <span class="text-xl font-bold h-5">{{ formatTimeRemaining }}</span>
            <p class="text-sm">
                remaining
            </p>
        </div> -->

        <!-- <UProgress color="info"></UProgress> -->
        <div class="flex gap-4 w-full">
            <div class="flex-1 flex flex-col items-center py-1 border border-slate-800 rounded-lg">
                <p class="text-xs">Completed</p>
                <p class="text-xl font-bold">{{ (state as any).current_cycle }}/{{ (state as any).total_cycles
                }}</p>
            </div>
            <div class="flex-1 flex flex-col items-center py-1 border border-slate-800 rounded-lg">
                <p class="text-xs">Current</p>
                <p class="text-xl font-bold">{{ currentDisplay }} A</p>
            </div>
        </div>
        <div class="flex gap-4 w-full">
            <div class="flex-1 flex flex-col items-center py-1 border border-slate-800 rounded-lg">
                <p class="text-xs">Phase</p>
                <p class="text-xl font-bold">{{ (state as any).phase }}</p>
            </div>
            <div class="flex-1 flex flex-col items-center py-1 border border-slate-800 rounded-lg">
                <p class="text-xs">Remaining</p>
                <p class="text-xl font-bold">{{ formatTimeRemaining }}</p>
            </div>
        </div>
        <UButton size="lg" color="error" class="w-full font-bold justify-center cursor-pointer" icon="i-ph-x-bold"
            @click="handleCancel">
            Cancel test
        </UButton>
    </div>
</template>

<!-- <template>
    <div class="flex-1 flex flex-col justify-between rounded-xl h-full p-4 bg-white/5 backdrop-blur box-shadow-lg">
        <UFormField label="Total cycles" size="sm">
            <UInputNumber size="lg" v-model="form.total_cycles" class="w-full" color="neutral" :min="10" :step="10" />
        </UFormField>
        <div class="flex gap-4">
            <UFormField class="flex-1" label="Actuate time" size="sm">
                <UInputNumber size="lg" v-model="form.actuate_time" class="w-full" color="neutral" :min="0" :step="1" />
            </UFormField>
            <UFormField class="flex-1" label="Rest time" hint="mins" size="sm">
                <UInputNumber size="lg" v-model="form.rest_time" class="w-full" color="neutral" :min="0" :step="1" />
            </UFormField>
        </div>
        <UFormField label="Current cutoff" hint="amps" size="sm">
            <UInputNumber size="lg" v-model="form.current_cutoff" class="w-full" color="neutral" :min="1" :max="30"
                :step="1" />
        </UFormField>
    </div>
</template> -->

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useSocket } from '~/composables/useSocket'

const { state, handleCancel } = useSocket()
const currentTime = ref(Date.now())

let timer: NodeJS.Timeout | null = null

onMounted(() => {
    timer = setInterval(() => {
        currentTime.value = Date.now()
    }, 1000)
})

onUnmounted(() => {
    if (timer) {
        clearInterval(timer)
    }
})

const formatTimeRemaining = computed(() => {
    const phase = (state.value as any).phase
    const phaseEndsAt = (state.value as any).phase_ends_at

    if (phase === 'idle' || !phaseEndsAt) {
        return '0:00'
    }

    const remaining = Math.max(0, phaseEndsAt - currentTime.value / 1000)
    const minutes = Math.floor(remaining / 60)
    const seconds = Math.floor(remaining % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

const currentDisplay = computed(() => {
    const val = (state.value as any).current
    if (typeof val === 'number' && !isNaN(val)) {
        return val.toFixed(1)
    }
    return '0.0'
})

const data = ref([
    {
        id: '4600',
        date: '2024-03-11T15:30:00',
        status: 'paid',
        email: 'james.anderson@example.com',
        amount: 594
    }
])
</script>
