// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  compatibilityDate: '2025-07-15',
  modules: ['../../../nuxt_django/src/module', '@nuxt/ui'],
  css: ['~/assets/css/main.css'],
  nuxtDjango: {},
  devtools: { enabled: true },
  runtimeConfig: {
    public: {
    }
  }
})
