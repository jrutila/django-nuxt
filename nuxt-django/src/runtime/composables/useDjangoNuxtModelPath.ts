import { useNuxtApp, useRuntimeConfig } from "nuxt/app"
import type { Ref } from "vue"
import { isRef, computed } from "vue"

const _modelPathCache = new Map<string, string>()

export const useDjangoNuxtModelPath = (model: any | Ref<any>, idOrQuery: any | Ref<any> | null = null) => {
  return computed(() => {
    if (isRef(model)) {
      model = model.value
    }
    if (isRef(idOrQuery)) {
      idOrQuery = idOrQuery.value
    }

    let id = null
    if (idOrQuery) {
      if (typeof idOrQuery === 'object') {
        id = idOrQuery.id
      } else {
        id = idOrQuery
      }
    }

    function resolveRefsInObject(obj: any) {
      if (isRef(obj)) {
        obj = obj.value
      }
      if (typeof obj === 'object') {
        return Object.fromEntries(Object.entries(obj).map(([key, value]) => [key, resolveRefsInObject(value)]))
      }
      return obj
    }

    const cacheKey = `${model}-${idOrQuery ? `${JSON.stringify(resolveRefsInObject(idOrQuery))}` : ''}`
    let path = _modelPathCache.get(cacheKey)
    if (!path) {
      const nuxtApp = useNuxtApp()
      if (nuxtApp['$djangoNuxtModelPath']) {
        path = nuxtApp['$djangoNuxtModelPath'](model, idOrQuery)
      } else {
        let baseUrl = useRuntimeConfig().public.nuxtDjango?.baseUrl || '/'
        if (nuxtApp['$djangoNuxtModelPathBaseUrl']) {
          baseUrl = nuxtApp['$djangoNuxtModelPathBaseUrl'](baseUrl, model, idOrQuery)
        }
        path = `${baseUrl.replace(/\/$/, '')}/${model}/${id ? `${id}/` : ''}`
      }
      if (path) {
        _modelPathCache.set(cacheKey, path)
      }
    }
    return path
  })
}