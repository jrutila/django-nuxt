import { useNuxtApp, useRuntimeConfig } from "nuxt/app"
import type { Ref } from "vue"
import { isRef } from "vue"

const _modelPathCache = new Map<string, string>()

export const useDjangoNuxtModelPath = (model: any | Ref<any>, id: any | Ref<any> | null = null) => {
  if (isRef(model)) {
    model = model.value
  }
  if (isRef(id)) {
    id = id.value
  }

  const cacheKey = `${model}-${id ? `${id}` : ''}`
  let path = _modelPathCache.get(cacheKey)
  if (!path) {
    const nuxtApp = useNuxtApp()
    if (nuxtApp['$djangoNuxtModelPath']) {
      path = nuxtApp['$djangoNuxtModelPath'](model, id)
    } else {
      const apiPath = useRuntimeConfig().public.nuxtDjango?.apiPath || '/api/'
      path = `${apiPath}${model}/${id ? `${id}/` : ''}`
    }
    if (path) {
      _modelPathCache.set(cacheKey, path)
    }
  }
  return path
}