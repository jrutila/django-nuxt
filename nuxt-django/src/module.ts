import { defineNuxtModule, addPlugin, createResolver, addImports, addTypeTemplate, addVitePlugin } from '@nuxt/kit'

function djangoPageHosts(origin: URL): string[] {
  const port = origin.port
  const hosts = new Set<string>()
  for (const hostname of [origin.hostname, 'localhost', '127.0.0.1']) {
    if (hostname) {
      hosts.add(port ? `${hostname}:${port}` : hostname)
    }
  }
  return [...hosts]
}

/** @nuxt/devtools only allows RPC when Origin host === WS Host. Rewrite Django origins to the Nuxt listen host. */
function allowDjangoDevtoolsRpc(server: { ws: { on: (...args: any[]) => any } }, allowedHosts: string[]) {
  const allowed = new Set(allowedHosts)
  const originalOn = server.ws.on.bind(server.ws)
  server.ws.on = (event: string, listener: (...args: any[]) => void) => {
    if (event !== 'connection') {
      return originalOn(event, listener)
    }
    return originalOn(event, (socket: unknown, request: { headers: Record<string, string | string[] | undefined> }) => {
      const originHeader = request.headers.origin
      const host = request.headers.host
      if (typeof originHeader === 'string' && typeof host === 'string') {
        try {
          const originUrl = new URL(originHeader)
          if (allowed.has(originUrl.host)) {
            request.headers.origin = `${originUrl.protocol}//${host}`
          }
        }
        catch {
          // ignore invalid Origin
        }
      }
      return listener(socket, request)
    })
  }
}

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

      nuxt.options.vite = nuxt.options.vite || {}
      const viteServer = nuxt.options.vite.server = nuxt.options.vite.server || {}

      // Vite modules/fonts redirect to :3000; HMR stays on Nuxt. Allow the Django
      // page origin for module CORS and DevTools RPC (Origin host must match WS Host).
      const pageHosts = djangoPageHosts(origin)
      if (viteServer.cors === undefined) {
        viteServer.cors = { origin: pageHosts.map(host => `${origin.protocol}//${host}`) }
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

      addVitePlugin({
        name: 'nuxt-django:devtools-origin',
        enforce: 'pre',
        configureServer(server) {
          allowDjangoDevtoolsRpc(server, pageHosts)
        },
      })
    }
  },
})
