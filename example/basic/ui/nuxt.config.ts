// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  compatibilityDate: '2025-07-15',
  modules: ['../../../nuxt_django/src/module'],
  nuxtDjango: {},
  devtools: { enabled: true }
})
