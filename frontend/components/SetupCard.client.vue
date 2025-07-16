<template>
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

        <!-- <UDrawer title="Are you sure?" should-scale-background> -->
        <UButton @click="handleStart(form)" size="lg" color="info"
            class="w-full font-bold justify-center cursor-pointer" icon="i-ph-play-bold">
            Start test
        </UButton>
        <!-- 
            <template #body>
                <p class="text-sm mb-4">Please ensure the cage is free of any objects or personnel. The tower will
                    repeatedly cycle until the test is cancelled or completed.
                </p>
                <UButton size="lg" color="info" class="w-full font-bold justify-center cursor-pointer"
                    @click="handleStart(form)">
                    Continue
                </UButton>
            </template>
</UDrawer> -->
    </div>
</template>

<script setup lang="ts">
const { handleStart } = useSocket()

const form = ref({
    total_cycles: 500,
    actuate_time: 2,
    rest_time: 18,
    current_cutoff: 16
})
</script>
