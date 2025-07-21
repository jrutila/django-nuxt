import { defineNuxtPlugin, useRuntimeConfig } from '#app'

export default defineNuxtPlugin(() => {
  console.log('django-drf-csrf plugin')
  globalThis.$fetch = $fetch.create({
    onRequest({ request, options }) {
      const config = useRuntimeConfig()
      const apiPath = config.public.nuxtDjango?.apiPath || '/api/'
      console.log('onRequest', apiPath, request)

      if (!request.startsWith(apiPath)) {
        return
      }

      if (options.method && options.method !== "GET") {
        const baseURL = config.public.nuxtDjango?.baseURL || '/'
        options.baseURL = baseURL

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
