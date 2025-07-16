import { ref, watch } from 'vue'
import { useWebSocket } from '@vueuse/core'

const state = ref({ status: 'idle' })
const socketStatus = ref<'CONNECTING' | 'OPEN' | 'CLOSING' | 'CLOSED'>('CONNECTING')

let socket: ReturnType<typeof useWebSocket> | null = null

if (import.meta.client) {
    socket = useWebSocket(`ws://${window.location.hostname}:8000/ws`, {
        autoReconnect: true,
        onMessage: (_, event) => {
            try {
                const data = JSON.parse(event.data)
                Object.assign(state.value, data)
            } catch {
                // Ignore parsing errors
            }
        }
    })

    if (socket) {
        watch(() => socket!.status.value, (newStatus) => {
            socketStatus.value = newStatus
        })
    }
}

function handleStart(params: { total_cycles: number; actuate_time: number; rest_time: number; current_cutoff: number }) {
    if (import.meta.client && socket && socketStatus.value === 'OPEN') {
        socket.send(JSON.stringify({ action: 'start', ...params }))
    }
}

function handleCancel() {
    if (import.meta.client && socket && socketStatus.value === 'OPEN') {
        socket.send(JSON.stringify({ action: 'cancel' }))
    }
}

function handleReset() {
    if (import.meta.client && socket && socketStatus.value === 'OPEN') {
        socket.send(JSON.stringify({ action: 'reset' }))
    }
}

function handleManualExtend(isDown: boolean) {
    if (import.meta.client && socket && socketStatus.value === 'OPEN') {
        socket.send(JSON.stringify({ action: isDown ? 'manual_extend' : 'manual_stop' }))
    }
}
function handleManualRetract(isDown: boolean) {
    if (import.meta.client && socket && socketStatus.value === 'OPEN') {
        socket.send(JSON.stringify({ action: isDown ? 'manual_retract' : 'manual_stop' }))
    }
}

export function useSocket() {
    return {
        state,
        socketStatus,
        handleStart,
        handleCancel,
        handleReset,
        handleManualExtend,
        handleManualRetract
    }
}