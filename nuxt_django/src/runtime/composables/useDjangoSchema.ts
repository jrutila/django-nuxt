import type { FetchError } from "ofetch"
import type { AsyncData } from "nuxt/app"

type DjangoSchema = any

type ReturnType = AsyncData<DjangoSchema, FetchError>

export const useDjangoSchema = async (model: string): Promise<ReturnType> => {
  const config = useRuntimeConfig()
  const schemaKey = config.public.nuxtDjango?.schemaKey || 'schema'
  const schema = useDjangoNuxt().value[schemaKey]
  const error = ref(null)
  const data = ref(null)
  if (!schema) {
    error.value = new Error(`Schema key ${schemaKey} not found`)
    return {
      data: data,
      error: error,
    }
  }
  if (!schema[model]) {
    error.value = new Error(`Model ${model} not found in schema`)
    return {
      data: data,
      error: error,
    }
  }
  data.value = schema[model]
  return {
    data: data,
    error: error,
  }
}
