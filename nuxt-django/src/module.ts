import { defineNuxtModule, addPlugin, createResolver, addImports, addTypeTemplate } from '@nuxt/kit'

// Module options TypeScript interface definition
export interface ModuleOptions {
  schemaKey?: string
  apiPath?: string
  baseURL?: string
  /** Public Django origin the browser uses in development. Default http://localhost:8000 */
  devOrigin?: string
}

export interface NuxtDjangoRuntimeConfig {
  schemaKey?: string
  apiPath?: string
  baseURL?: string
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
    addTypeTemplate({
      filename: 'types/nuxt-django.d.ts',
      getContents: () => `import type { $Fetch } from 'ofetch'

declare module '#app' {
  interface NuxtApp {
    $djangoApi: $Fetch
  }
}
`,
    })
    nuxt.options.optimization = nuxt.options.optimization || {}
    nuxt.options.optimization.keyedComposables = nuxt.options.optimization.keyedComposables || []
    nuxt.options.optimization.keyedComposables.push({
      name: 'useDjangoApi',
      argumentLength: 2,
    })
    addImports([
      'useDjangoApi', 'useDjangoNuxt', 'useDjangoSchema', 'useDjangoModel', 'useDjangoNuxtModelPath',
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

    if (nuxt.options.dev) {
      const devOrigin = options.devOrigin || process.env.NUXT_DJANGO_DEV_ORIGIN || 'http://localhost:8000'
      let origin: URL
      try {
        origin = new URL(devOrigin)
      }
      catch {
        origin = new URL('http://localhost:8000')
      }

      const isHttps = origin.protocol === 'https:'
      const clientPort = origin.port ? Number(origin.port) : (isHttps ? 443 : 80)

      nuxt.options.vite = nuxt.options.vite || {}
      const viteServer = nuxt.options.vite.server = nuxt.options.vite.server || {}
      if (!viteServer.origin) {
        viteServer.origin = origin.origin
      }

      if (viteServer.hmr !== false) {
        const existingHmr = typeof viteServer.hmr === 'object' && viteServer.hmr ? viteServer.hmr : {}
        viteServer.hmr = {
          protocol: isHttps ? 'wss' : 'ws',
          clientPort,
          ...existingHmr,
        }
      }

      if (viteServer.allowedHosts !== true) {
        const hosts = Array.isArray(viteServer.allowedHosts) ? [...viteServer.allowedHosts] : []
        for (const host of [origin.hostname, 'localhost', '127.0.0.1']) {
          if (host && !hosts.includes(host)) {
            hosts.push(host)
          }
        }
        viteServer.allowedHosts = hosts
      }
    }
  },
})
