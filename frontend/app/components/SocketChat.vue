<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'

const WS_URL = 'ws://localhost:8000/ws/chat'

const messages = ref([])
const input = ref('')
const ws = ref(null)
const loading = ref(false)
const currentBotId = ref(null)

const box = ref(null)
const ta = ref(null)

const id = () => Date.now() + Math.random()

function scroll() {
  nextTick(() => {
    if (box.value) box.value.scrollTop = box.value.scrollHeight
  })
}

function resize() {
  nextTick(() => {
    if (!ta.value) return
    ta.value.style.height = 'auto'
    ta.value.style.height = ta.value.scrollHeight + 'px'
  })
}

function connect() {
  ws.value = new WebSocket(WS_URL)

  ws.value.onmessage = (e) => {
    const data = JSON.parse(e.data)

    if (data.type === 'chunk') {
      if (!currentBotId.value) {
        currentBotId.value = id()
        messages.value.push({
          id: currentBotId.value,
          role: 'bot',
          content: ''
        })
      }

      const msg = messages.value.find(x => x.id === currentBotId.value)
      if (msg) msg.content += data.content
      scroll()
    }

    if (data.type === 'done') {
      loading.value = false
      currentBotId.value = null
      scroll()
    }

    if (data.type === 'error') {
      loading.value = false
      currentBotId.value = null
      messages.value.push({
        id: id(),
        role: 'bot',
        content: 'Ошибка: ' + data.content
      })
      scroll()
    }
  }

  ws.value.onclose = () => {
    messages.value.push({
      id: id(),
      role: 'bot',
      content: 'Соединение отвалилось'
    })
    loading.value = false
    currentBotId.value = null
    scroll()
  }
}

function send() {
  const text = input.value.trim()
  if (!text || !ws.value || ws.value.readyState !== 1 || loading.value) return

  messages.value.push({
    id: id(),
    role: 'user',
    content: text
  })

  ws.value.send(text)
  input.value = ''
  loading.value = true
  currentBotId.value = null

  resize()
  scroll()
}

// function onKey(e) {
//   if (e.key === 'Enter' && !e.shiftKey) {
//     e.preventDefault()
//     send()
//   }
// }

onMounted(() => {
  connect()
  resize()
})

onBeforeUnmount(() => {
  if (ws.value) ws.value.close()
})
</script>

<template>
  <div class="min-h-screen text-white p-6">
    <div class="mx-auto">
      <h1 class="text-xl font-bold mb-6">Чат с GPT</h1>

      <div ref="box" class="bg-zinc-900/90 rounded-t-2xl p-4 md:h-[60vh] overflow-y-auto  border border-zinc-800">
        
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="whitespace-pre-wrap"
          :class="msg.role === 'user' ? 'text-blue-300' : 'text-zinc-100'"
        >
          <span class="font-bold">
            {{ msg.role === 'user' ? 'Ты:' : 'Агент:' }}
          </span>
          {{ msg.content }}
        </div>
      </div>

      <div class="grid grid-cols-1">
        <textarea
          v-model="input"
          rows="3"
          placeholder="Написать агенту..."
          class="flex-1 rounded-b-xl bg-zinc-800/95 border border-zinc-700 px-4 py-3 outline-none"
          @keydown.enter.exact.prevent="send"
        />

        <div class="mt-1 flex justify-center">
          <button
            class="px-6 p-2 rounded-full bg-blue-600 hover:bg-blue-500 transition"
            @click="send"
          >
            Отправить
          </button>          
        </div>

      </div>
    </div>
  </div>
</template>