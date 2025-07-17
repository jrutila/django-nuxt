import { defineNuxtModule, addPlugin, createResolver, addImportsDir } from '@nuxt/kit'

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
    addPlugin(resolver.resolve('./runtime/plugin'))
    addImportsDir(resolver.resolve('./runtime/composables/'), { prepend: true })
    nuxt.options.runtimeConfig.public.nuxtDjango = (nuxt.options.runtimeConfig.public.nuxtDjango || {}) as NuxtDjangoRuntimeConfig
    nuxt.options.runtimeConfig.public.nuxtDjango.schemaKey = options.schemaKey || '{{ NUXT_DJANGO_SCHEMA_KEY }}'
  },
})
