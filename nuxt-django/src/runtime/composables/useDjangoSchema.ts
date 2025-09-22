import type { FetchError } from "ofetch"
import { useRuntimeConfig } from "#app"
import { ref } from "vue"
import { useDjangoNuxt } from "./useDjangoNuxt"
import { useDjangoNuxtModelPath } from "./useDjangoNuxtModelPath"
import { useFetch } from "nuxt/app"
import type { AsyncData } from "nuxt/app"

type DjangoSchema = Record<string, any>

type ReturnType = AsyncData<DjangoSchema, FetchError>

export const useDjangoSchema = async (model: string, query: Record<string, Ref<any>> = {}): Promise<ReturnType> => {
  const error = ref(null as FetchError | null)
  const data = ref(null as DjangoSchema | null)

  if (Object.keys(query).length === 0) {
    const config = useRuntimeConfig()
    const schemaKey = config.public.nuxtDjango?.schemaKey || 'schema'
    const schema = useDjangoNuxt().value[schemaKey]
    if (!schema) {
      error.value = new Error(`Schema key ${schemaKey} not found`)
    } else if (!schema[model]) {
      error.value = new Error(`Model ${model} not found in schema`)
    }
    data.value = schema[model]
  }
  if (error.value || Object.keys(query).length > 0) {
    const path = useDjangoNuxtModelPath(model)
    return { ...(await useFetch<any>(path, {
      query: query,
      method: 'OPTIONS',
      transform: (data) => {
        data['~standard'].validate = new Function('value', data['~standard'].validate)
        return data
      }
    })) }
  }
  return {
    data: data,
    error: error,
  }
}
