<script setup>

  const config = useRuntimeConfig()

  const url = ref("https://tehnosvar.ru/products/svarochniemachiny/tochechnaya/tochechnay/100/")
  const result = ref(null)

  const checkSecret = async () => {
    const data = await $fetch(`${config.public.baseURL}/seo/meta`, {
      method: 'POST',
      body: {
        url: url.value
      },
    })
    console.log(data)
    result.value = data
  }

</script>


<template>
  <div class="bg-gray-700 h-screen text-white mx-auto px-12 py-4">
    <p class="text-white text-4xl mb-6">Анализ SEO</p>
    <input v-model="url" type="text" placeholder="Введите адрес страницы" class="mb-4 p-2 rounded text-black w-full"/>

    <button @click="checkSecret" class="bg-blue-500 text-white px-4 py-2 rounded">Проверить META-теги</button>

    <div v-if="result" class="mt-6">

      <div class="bg-gray-800 p-4 rounded-xl">
        <p class="text-xs text-gray-400">Техническая информация для отладки:</p>
        <div class="">
          <p  class="py-1 text-xs">{{ result }}</p>          
        </div>
      </div>


      <div class="bg-gray-800 p-4 rounded-xl mt-6">
        <div class="grid grid-cols-1 gap-8">

          <div class="grid grid-cols-1 gap-1">
            <div class="text-sm text-gray-400">
              <p>МЕТА заголовок (title): </p>
            </div>
            <div class="text-base text-gray-100">
              <p>{{ result.title }}</p>
            </div>      
          </div>
            
          <div class="grid grid-cols-1 gap-1">
            <div class="text-sm text-gray-400">
              <p>МЕТА описание (description):</p>
            </div>
            <div class="text-base text-gray-100">
              <p>{{ result.description }}</p>
            </div>      
          </div>

          <div class="grid grid-cols-1 gap-1">
            <div class="text-sm text-gray-400">
              <p>МЕТА ключевые слова (keywords):</p>
            </div>
            <div class="text-base text-gray-100">
              <p>{{ result.keywords }}</p>
            </div>      
          </div>
        </div>



      </div>


    </div>

    <div v-else class="mt-6">
      <p class="text-gray-400">Результаты проверки будут отображены здесь.</p>
    </div>

  </div>
</template>