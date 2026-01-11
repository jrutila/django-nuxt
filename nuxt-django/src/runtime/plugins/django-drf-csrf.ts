import { defineNuxtPlugin, useRuntimeConfig } from '#app'
import { isRef } from 'vue'

export default defineNuxtPlugin(() => {
  globalThis.$fetch = $fetch.create({
    onRequest({ request, options }) {
      const config = useRuntimeConfig()
      const apiPath = config.public.nuxtDjango?.apiPath || '/api/'

      if (isRef(request)) {
        request = request.value
      }

      if (!request.startsWith(apiPath)) {
        return
      }

      const baseURL = config.public.nuxtDjango?.baseURL || '/'
      options.baseURL = baseURL

      if (options.method && options.method !== "GET") {
        const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1]
        if (csrftoken) {
          options.headers.set('X-CSRFToken', csrftoken)
        } else {
          console.error('No CSRF token found in cookies')
        }
      }
    }
  })
})
