import { createUseFetch, useNuxtApp } from '#app'

type CreateUseFetchWithFactory = typeof createUseFetch & {
  __nuxt_factory?: typeof createUseFetch
}

const createUseDjangoApi = (createUseFetch as CreateUseFetchWithFactory).__nuxt_factory ?? createUseFetch

export const useDjangoApi = createUseDjangoApi(callerOptions => ({
  $fetch: useNuxtApp().$djangoApi as typeof $fetch,
  ...callerOptions,
}))
