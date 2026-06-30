// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/color-mode',
    '@nuxtjs/i18n',
    '@nuxtjs/robots',
    '@nuxtjs/sitemap',
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    'nuxt-mdi'
  ],

  runtimeConfig: {
    public: {
      baseURL: "http://127.0.0.1:8000",
      SOCKET: "ws://127.0.0.1:8000/ws/chat",
    },
  },

})