export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.provide('djangoNuxtModelPath', (model: string, id: string | null = null) => {
    return `/api/${model}/${id ? `${id}/` : ''}` + `?custom=modelPath`
  })
})