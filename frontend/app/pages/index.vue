<script setup>

  const config = useRuntimeConfig()

  const url = ref("https://tehnosvar.ru/products/svarochniemachiny/tochechnaya/tochechnay/100/")
  const result = ref(null)

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

  const checkSecret = async () => {
    const data = await $fetch(`${config.public.baseURL}/seo/meta`, {
      method: 'POST',
      body: {
        url: url.value
      },
    })
    console.log(data)
    result.value = data
    url.value = null
  }

</script>


<template>
  <div class="bg-gray-700 min-h-screen text-white mx-auto px-12 py-4">
    <p class="text-white text-4xl mb-6">Анализ SEO</p>
    <input v-model="url" type="text" placeholder="Вставьте url адрес страницы" class="mb-4 p-2 rounded text-black w-full"/>

    <button @click="checkSecret" class="bg-blue-500 text-white px-4 py-2 rounded">Проверить META-теги</button>

    <div v-if="result" class="mt-6">


      <div class="grid grid-cols-1 gap-1 mt-6 px-0.5">
        <div class="text-sm text-gray-400">
          <p>Заголовок (H1): </p>
        </div>
        <div class="text-xl text-gray-100">
          <p>{{ result.h1 }}</p>
        </div>      
      </div>


      <div class="bg-gray-800 p-4 rounded-xl shadow-md shadow-black/40 mt-6">
        <div class="grid grid-cols-1 gap-8">

          <div class="grid grid-cols-1 gap-1">
            <div class="text-sm text-gray-400">
              <p>МЕТА заголовок (title): </p>
            </div>
            <div class="grid grid-cols-1 gap-2 text-base text-gray-100">
              <p>{{ result.title }}</p>
              <p class="text-xs text-gray-500">Кол-во символов: {{ result.title.length }} / Рекомендуемое: 50-60</p>
            </div>      
          </div>
            
          <div class="grid grid-cols-1 gap-1">
            <div class="text-sm text-gray-400">
              <p>МЕТА описание (description):</p>
            </div>
            <div class="grid grid-cols-1 gap-2 text-base text-gray-100">
              <!-- <p v-html="highlightWords(result.description)"></p> -->
              <p>{{ result.description }}</p>
              <p class="text-xs text-gray-500">Кол-во символов: {{ result.description.length }} / Рекомендуемое: 150-160</p>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-1">
            <div class="text-sm text-gray-400">
              <p>МЕТА ключевые слова (keywords):</p>
            </div>
            <div class="grid grid-cols-1 gap-2 text-base text-gray-100">
              <p>{{ result.keywords }}</p>
              <p class="text-xs text-gray-500">Кол-во символов: {{ result.keywords.length }} / Рекомендуемое: 150-160</p>
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
        <p class="text-xs text-gray-100">Анализ SEO заданной страницы...</p>
      </div>





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