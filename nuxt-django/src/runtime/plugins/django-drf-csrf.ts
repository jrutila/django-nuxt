import { defineNuxtPlugin, useRuntimeConfig } from '#app'

export default defineNuxtPlugin(() => {
  const djangoApi = $fetch.create({
    onRequest({ options }) {
      const config = useRuntimeConfig()
      const baseURL = config.public.nuxtDjango?.baseURL || '/'
      options.baseURL = baseURL

      if (import.meta.client && options.method && options.method !== 'GET') {
        const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1]
        if (csrftoken) {
          options.headers.set('X-CSRFToken', csrftoken)
        } else {
          console.error('No CSRF token found in cookies')
        }
      }
    },
  })

  return {
    provide: {
      djangoApi,
    },
  }
})
