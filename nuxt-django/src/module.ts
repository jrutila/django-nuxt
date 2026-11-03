import { createRequire } from 'node:module'
import { existsSync, readFileSync, realpathSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
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
  /** Django STATIC_URL. Default /static/. Also accepts static/ or a CDN URL. */
  staticUrl?: string
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

    // Production JS and CSS live under <STATIC_URL>_nuxt/, fonts under <STATIC_URL>_fonts/.
    // The HTML renderer reads runtimeConfig, which was already copied from the
    // default /_nuxt/ before modules run, so both copies have to change together.
    // Dev keeps /_nuxt/ and /_fonts/.
    if (!nuxt.options.dev) {
      const { cdnURL, path } = staticPublicBase(options.staticUrl)
      const appConfig = nuxt.options.runtimeConfig.app as { buildAssetsDir?: string, cdnURL?: string } | undefined
      const buildAssetsDir = nuxt.options.app.buildAssetsDir
      if (buildAssetsDir === '/_nuxt/' || buildAssetsDir === '/_nuxt') {
        const assetsDir = `${path}_nuxt/`
        nuxt.options.app.buildAssetsDir = assetsDir
        if (appConfig) {
          appConfig.buildAssetsDir = assetsDir
        }
      }
      if (cdnURL && !nuxt.options.app.cdnURL) {
        nuxt.options.app.cdnURL = cdnURL
        if (appConfig) {
          appConfig.cdnURL = cdnURL
        }
      }
      const fonts = (nuxt.options as { fonts?: { assets?: { prefix?: string } } }).fonts ??= {}
      fonts.assets ??= {}
      if (!fonts.assets.prefix) {
        fonts.assets.prefix = fontAssetsPrefix(nuxt.options.rootDir, path)
      }
    }

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

/** Path of STATIC_URL, plus a CDN origin when the value is absolute. */
function staticPublicBase(staticUrl: string | undefined): { cdnURL: string, path: string } {
  const raw = (staticUrl || '/static/').trim() || '/static/'
  let cdnURL = ''
  let path = raw
  if (raw.includes('://')) {
    const url = new URL(raw)
    cdnURL = url.origin
    path = url.pathname
  }
  if (!path.startsWith('/')) {
    path = `/${path}`
  }
  if (!path.endsWith('/')) {
    path = `${path}/`
  }
  return { cdnURL, path }
}

/** @nuxt/fonts 0.x uses this as the whole public path. 1.x joins it onto buildAssetsDir. */
function fontAssetsPrefix(rootDir: string, staticPath: string): string {
  if (installedFontsMajor(rootDir) === 0) {
    return `${staticPath.replace(/\/$/, '')}/_fonts`
  }
  return '_fonts'
}

function installedFontsMajor(rootDir: string): number | null {
  const starts = [resolve(rootDir, 'package.json')]
  const uiPackage = resolve(rootDir, 'node_modules/@nuxt/ui/package.json')
  if (existsSync(uiPackage)) {
    try {
      starts.unshift(realpathSync(uiPackage))
    }
    catch {
      starts.unshift(uiPackage)
    }
  }
  for (const start of starts) {
    if (!existsSync(start)) {
      continue
    }
    try {
      const entry = createRequire(start).resolve('@nuxt/fonts')
      const version = packageVersion(entry, '@nuxt/fonts')
      const major = Number.parseInt(version?.split('.')[0] ?? '', 10)
      if (!Number.isNaN(major)) {
        return major
      }
    }
    catch {
      // This start cannot see @nuxt/fonts.
    }
  }
  return null
}

function packageVersion(entry: string, name: string): string | undefined {
  let dir = dirname(entry)
  while (true) {
    const packagePath = resolve(dir, 'package.json')
    if (existsSync(packagePath)) {
      const pkg = JSON.parse(readFileSync(packagePath, 'utf8')) as { name?: string, version?: string }
      if (pkg.name === name) {
        return pkg.version
      }
    }
    const parent = dirname(dir)
    if (parent === dir) {
      return undefined
    }
    dir = parent
  }
}
