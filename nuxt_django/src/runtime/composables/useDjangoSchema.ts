import type { FetchError } from "ofetch"
import type { AsyncData } from "nuxt/app"

type DjangoSchema = any

type ReturnType = AsyncData<DjangoSchema, FetchError>

export const useDjangoSchema = async (model: string): Promise<ReturnType> => {
  const config = useRuntimeConfig()
  const schemaKey = config.public.nuxtDjango?.schemaKey || 'schema'
  const schema = useDjangoNuxt().value[schemaKey]
  if (!schema) {
    throw new Error(`Schema key ${schemaKey} not found`)
  }
  return {
    data: schema[model],
    error: null,
  }
}
