import { defineNuxtModule, addPlugin, createResolver, addImportsDir, addImports } from '@nuxt/kit'

// Module options TypeScript interface definition
export interface ModuleOptions {
  schemaKey?: string
}

export interface NuxtDjangoRuntimeConfig {
  schemaKey?: string
}

export default defineNuxtModule<ModuleOptions>({
  meta: {
    name: 'nuxt_django',
    configKey: 'nuxtDjango',
  },
  // Default configuration options of the Nuxt module
  defaults: {},
  setup(options, nuxt) {
    const resolver = createResolver(import.meta.url)

    // Do not add the extension since the `.ts` will be transpiled to `.mjs` after `npm run prepack`
    addPlugin(resolver.resolve('./runtime/plugins/django-drf-csrf'))
    addPlugin(resolver.resolve('./runtime/plugins/django-nuxt'))
    addImports([
      'useDjangoNuxt', 'useDjangoSchema', 'useDjangoModel', 'useDjangoNuxtModelPath',
    ].map(name => ({
      from: resolver.resolve(`./runtime/composables/${name}`),
      name,
      as: name,
    })))
    addImports([
      'createDjangoModel', 'updateDjangoModel', 'patchDjangoModel', 'deleteDjangoModel',
    ].map(name => ({
      from: resolver.resolve(`./runtime/utils/crud`),
      name,
      as: name,
    })))
    addImports([{
      from: resolver.resolve(`./runtime/utils/ui-form-server-errors`),
      name: 'handDjangoServerErrors',
      as: 'handDjangoServerErrors',
    }])
    nuxt.options.runtimeConfig.public.nuxtDjango = (nuxt.options.runtimeConfig.public.nuxtDjango || {}) as NuxtDjangoRuntimeConfig
    nuxt.options.runtimeConfig.public.nuxtDjango.schemaKey = options.schemaKey || '{{ NUXT_DJANGO_SCHEMA_KEY }}'
    nuxt.options.runtimeConfig.public.nuxtDjango.apiPath = options.apiPath || '{{ NUXT_DJANGO_API_PATH }}'
    nuxt.options.runtimeConfig.public.nuxtDjango.baseURL = options.baseURL || '{{ NUXT_DJANGO_BASE_URL }}'
  },
})
