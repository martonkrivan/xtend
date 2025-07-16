<template>
  <UApp>
    <Transition name="fade" appear>
      <div v-if="loading"
        class="fixed inset-0 z-50 bg-slate-950 flex items-center justify-center transition-opacity duration-500">
        <UIcon name="i-ph-arrows-clockwise-bold" class="size-8 text-white animate-spin" />
      </div>
    </Transition>
    <div
      class="flex h-screen w-screen select-none bg-slate-950 bg-[url('/assets/img/bg.svg')] bg-cover bg-center bg-no-repeat p-4 gap-4 overflow-hidden"
      data-vaul-drawer-wrapper>
      <div class="flex-1 flex flex-col justify-between gap-4">
        <div class="flex flex-col p-4 gap-4 pb-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 self-center flex-shrink-0" viewBox="0 0 338.867 53.733">
            <path
              d="M8.535 283.156s88.211-16.289 206.211-36.301c309.852-52.546 879.634-140.878 1079.544-117.359 93.51 10.945 137.44 38.899 161.35 62.02 10.4 10.019 25 29.507 32.91 34.539 7.03 5.191 17.17 7.785 31.03 7.343 13.78-.394 35.94-2.832 35.94-2.832L1406.13 0 0 251.566l8.535 31.59"
              style="fill:currentColor;fill-opacity:1;fill-rule:nonzero;stroke:none"
              transform="matrix(.13333 0 0 -.13333 0 53.733)" />
            <path
              d="M2533.05 119.875s-35.18 6.508-84.06 15.137c-248.22 43.926-971.1 165.633-1201.7 138.562-93.53-11.023-137.45-38.972-161.37-62.054-10.38-10.063-24.95-29.59-32.86-34.5-7.11-5.27-17.21-7.829-31.03-7.43-13.82.48-36.022 2.793-36.022 2.793L1135.4 402.988l1406.11-251.566-8.46-31.547"
              style="fill:currentColor;fill-opacity:1;fill-rule:nonzero;stroke:none"
              transform="matrix(.13333 0 0 -.13333 0 53.733)" />
          </svg>
          <h1 class="text-xl font-bold flex-grow text-center">Tower Cycle Tester</h1>
        </div>


        <div class="rounded-xl bg-white/5 backdrop-blur box-shadow-lg flex flex-col items-center p-4 gap-4 w-full">
          <div class="flex flex-col gap-2 w-full">
            <div class="flex justify-start items-center gap-2 -mt-2 -mr-4">
              <label class="text-xs font-bold uppercase tracking-wider flex-shrink-0">Manual Jog</label>
              <USeparator class="w-full" />
            </div>
            <div class="flex items-center gap-2">
              <USwitch color="info" v-model="manualDirection" />
              <span class="text-xs">Reverse Direction</span>
            </div>
            <UButton class="cursor-pointer font-bold" variant="outline" color="info" size="lg"
              icon="i-ph-arrows-out-simple-bold" :disabled="state.status === 'running'"
              @mousedown="manualDirection ? handleManualExtend(true) : handleManualRetract(true)"
              @mouseup="manualDirection ? handleManualExtend(false) : handleManualRetract(false)"
              @mouseleave="manualDirection ? handleManualExtend(false) : handleManualRetract(false)"
              @touchstart.prevent="manualDirection ? handleManualExtend(true) : handleManualRetract(true)"
              @touchend.prevent="manualDirection ? handleManualExtend(false) : handleManualRetract(false)">
              Extend
            </UButton>
            <UButton class="cursor-pointer font-bold" variant="outline" color="info" size="lg"
              icon="i-ph-arrows-in-simple-bold" :disabled="state.status === 'running'"
              @mousedown="manualDirection ? handleManualRetract(true) : handleManualExtend(true)"
              @mouseup="manualDirection ? handleManualRetract(false) : handleManualExtend(false)"
              @mouseleave="manualDirection ? handleManualRetract(false) : handleManualExtend(false)"
              @touchstart.prevent="manualDirection ? handleManualRetract(true) : handleManualExtend(true)"
              @touchend.prevent="manualDirection ? handleManualRetract(false) : handleManualExtend(false)">
              Retract
            </UButton>

          </div>

        </div>

      </div>
      <div class="flex-1">
        <Transition name="card-fade-slide" mode="out-in" appear>
          <component :is="currentCard" />
        </Transition>
      </div>
    </div>
  </UApp>
</template>

<script setup lang="ts">
import { useDateFormat, useNow } from '@vueuse/core'
import type { StepperItem } from '@nuxt/ui'
import { watch, ref } from 'vue'

import SetupCard from '~/components/SetupCard.client.vue'
import TestingCard from '~/components/TestingCard.client.vue'
import CompletedCard from '~/components/CompletedCard.client.vue'
import FailedCard from '~/components/FailedCard.client.vue'

const { state, socketStatus, handleStart, handleManualExtend, handleManualRetract } = useSocket()

const manualDirection = ref(true) // true = normal, false = swapped

const currentStep = ref(0)

const stepperStep = computed(() => {
  if (currentCard.value === SetupCard) return 0
  if (currentCard.value === TestingCard) return 1
  if (currentCard.value === CompletedCard || currentCard.value === FailedCard) return 2
})

const items = ref<StepperItem[]>([
  {
    title: 'Setup',
    icon: 'i-ph-wrench-bold',
    description: 'Input your desired test parameters and begin.',
  },
  {
    title: 'Testing',
    icon: 'i-ph-hourglass-bold'
  },
  {
    title: 'Results',
    icon: 'i-ph-file-text-bold'
  }
])

const currentCard = computed(() => {
  switch (state.value.status) {
    case 'running':
      return TestingCard
    case 'failed':
      return FailedCard
    case 'completed':
      return CompletedCard
    default:
      return SetupCard
  }
})

const formatted = useDateFormat(useNow(), 'H:mm')

const loading = ref(true)

watch(
  () => state.value.status,
  (val) => {
    if (val !== undefined && loading.value) {
      setTimeout(() => {
        loading.value = false
      }, 1000)
    }
  },
  { immediate: true }
)
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
}
</style>
