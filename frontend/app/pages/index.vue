<script setup>

  import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'



  const config = useRuntimeConfig()

  const messages = ref([])
  const input = ref('')
  const ws = ref(null)
  const loading = ref(false)
  const currentBotId = ref(null)

  const box = ref(null)
  const ta = ref(null)

  const id = () => Date.now() + Math.random()


  const result = ref(null)

  
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
    ws.value = new WebSocket(`${config.public.SOCKET}/ws/chat`)

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
    // const text = input.value.trim()

    const url = new URL(result.value?.url)
    const domain = url.hostname

    const text = `
    Адрес страницы: ${domain}
    Заголовок : ${result.value?.title}
    Описание : ${result.value?.description}
    Ключевые слова : ${result.value?.keywords}
    
    `
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






  const url = ref(null)


  const highlightWords = (value) => {
    if (!value) return ''

    const escaped = String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')

    return escaped.replace(
      /(?<![\p{L}\p{N}_])(машина|переменным)(?![\p{L}\p{N}_])/giu,
      '<mark class="bg-yellow-300 text-gray-900 px-0.5">$1</mark>'
    )
  }

  const getData = ref(false)
  const checkSecret = async () => {
    getData.value = true
    const data = await $fetch(`${config.public.baseURL}/seo/meta`, {
      method: 'POST',
      body: {
        url: url.value
      },
    })
    console.log(data)
    result.value = data
    url.value = null
    messages.value = []
    getData.value = false
    send()
  }

</script>


<template>
  <div class="bg-gray-700 min-h-screen text-white mx-auto px-12 py-4">
    <p class="text-white text-4xl mb-6">Анализ SEO</p>
    <input v-model="url" type="text" placeholder="Вставьте url адрес страницы" class="mb-4 p-2 rounded text-black w-full"/>

    <div>
      <button @click="checkSecret" :disabled="getData" class="bg-blue-500 hover:bg-blue-600 active:bg-blue-700 border border-blue-400 text-white w-52 px-2 py-1 rounded transition-all">
        <p v-if="getData">Запрос...</p>          
        <p v-else>Проверить META-теги</p>

      </button>
    </div>

    <div v-if="result" class="mt-6">


      <div class="grid grid-cols-1 gap-1 mt-6 px-0.5">
        <div class="text-sm text-gray-400">
          <p>Заголовок (H1): </p>
        </div>
        <div v-if="result.h1" class="text-xl text-gray-100">
          <p>{{ result.h1 }}</p>
        </div>      
      </div>


      <div class="bg-gray-800 p-4 rounded-xl shadow-md shadow-black/40 mt-6">
        <div class="grid grid-cols-1 gap-8">

          <div class="grid grid-cols-1 gap-1">
            <div class="text-sm text-gray-400">
              <p>МЕТА заголовок (title): </p>
            </div>
            <div v-if="result.title" class="grid grid-cols-1 gap-2 text-base text-gray-100">
              <p>{{ result.title }}</p>
              <p class="text-xs text-gray-500">Кол-во символов: {{ result.title.length }} / Рекомендуемое: 50-60</p>
            </div>
            <div v-else>
              <p class="text-xs text-gray-300 mt-2">( Отсутствует )</p>
            </div>      
          </div>
            
          <div class="grid grid-cols-1 gap-1">
            <div class="text-sm text-gray-400">
              <p>МЕТА описание (description):</p>
            </div>
            <div v-if="result.description" class="grid grid-cols-1 gap-2 text-base text-gray-100">
              <!-- <p v-html="highlightWords(result.description)"></p> -->
              <p>{{ result.description }}</p>
              <p class="text-xs text-gray-500">Кол-во символов: {{ result.description.length }} / Рекомендуемое: 150-160</p>
            </div>
            <div v-else>
              <p class="text-xs text-gray-300 mt-2">( Отсутствует )</p>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-1">
            <div class="text-sm text-gray-400">
              <p>МЕТА ключевые слова (keywords):</p>
            </div>
            <div v-if="result.keywords" class="grid grid-cols-1 gap-2 text-base text-gray-100">
              <p>{{ result.keywords }}</p>
              <p class="text-xs text-gray-500">Кол-во символов: {{ result.keywords.length }} / Рекомендуемое: 150-160</p>
            </div>
            <div v-else>
              <p class="text-xs text-gray-300 mt-2">( Отсутствует )</p>
            </div>
          </div>
        </div>


      </div>




      <div class="grid grid-cols-1 gap-1 mt-6 px-0.5">
        <div class="py-4">
          <p class="text-xl text-gray-100">Обзор от ИИ: </p>
        </div>     
      </div>
      <div class="bg-gray-800 p-4 rounded-xl shadow-md shadow-black/40 min-h-52">
        <div v-if="messages.length > 0">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="whitespace-pre-wrap"
            :class="msg.role === 'user' ? 'hidden' : 'text-zinc-100'"
          >
            <!-- <span class="font-bold">
              {{ msg.role === 'user' ? 'Ты:' : 'Агент:' }}
            </span> -->
            {{ msg.content }}
          </div>
        </div>
        <div v-else>
          <p class="text-xs text-gray-300 mt-2">( Отсутствует )</p>
        </div>

        <!-- <textarea
          v-model="input"
          rows="3"
          placeholder="Написать агенту..."
          class="flex-1 rounded-b-xl bg-zinc-800/95 border border-zinc-700 px-4 py-3 outline-none"
          @keydown.enter.exact.prevent="send"
        /> -->
      </div>


      <!-- <div class="mt-1 py-4 flex justify-center">
        <button
          class="px-6 p-2 rounded-full bg-blue-600 hover:bg-blue-500 transition"
          @click="send"
        >
          Анализировать
        </button>          
      </div> -->


      <div class="bg-gray-800 p-4 rounded-xl shadow-md shadow-black/40 mt-24">
        <p class="text-xs text-gray-400">Техническая информация для отладки:</p>
        <div class="">
          <p  class="py-1 text-xs">{{ result }}</p>          
        </div>
      </div>



    </div>

    <div v-else class="mt-6">
      <p class="text-gray-400">Результаты проверки будут отображены здесь.</p>
    </div>

  </div>
</template>