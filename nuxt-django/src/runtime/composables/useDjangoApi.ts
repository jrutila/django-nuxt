import { createUseFetch } from '#app/composables/fetch'
import { useNuxtApp } from '#app'
import type { useFetch } from 'nuxt/app'

type CreateUseFetchWithFactory = typeof createUseFetch & {
  __nuxt_factory?: typeof createUseFetch
}

const createUseDjangoApi = (createUseFetch as CreateUseFetchWithFactory).__nuxt_factory ?? createUseFetch

export const useDjangoApi: typeof useFetch = createUseDjangoApi(callerOptions => ({
  $fetch: useNuxtApp().$djangoApi as typeof $fetch,
  ...callerOptions,
}))
