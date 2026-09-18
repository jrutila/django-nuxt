# Nuxt Django

Nuxt module for integrating Nuxt frontend code with Django-Nuxt backend projects.

This package is maintained in the `django-nuxt` monorepo:

- Repository: <https://github.com/jrutila/django-nuxt>
- npm package (GitHub Packages): <https://github.com/jrutila/django-nuxt/pkgs/npm/nuxt-django>

## Install

```bash
npm install @jrutila/nuxt-django
```

## Usage

Add the module to your `nuxt.config.ts`:

```ts
export default defineNuxtConfig({
  modules: ['@jrutila/nuxt-django'],
})
```

Optional runtime settings can be configured with `nuxtDjango`:

```ts
export default defineNuxtConfig({
  modules: ['@jrutila/nuxt-django'],
  nuxtDjango: {
    schemaKey: '...',
    apiPath: '/api/',
    baseURL: 'http://localhost:8000',
    // Public origin the browser uses in development (Django). Default: http://localhost:8000
    devOrigin: 'http://localhost:8000',
  },
})
```

In development, Vite modules and fonts load from Nuxt (port 3000). `devOrigin` / `NUXT_DJANGO_DEV_ORIGIN` is the Django page origin (default `http://localhost:8000`) so Vite `allowedHosts` and CORS accept DevTools RPC proxied through Django.

Requires Nuxt **4.4+** for `useDjangoApi` (`createUseFetch`).

## Calling the Django API

The module does not modify global `$fetch` or `useFetch`. Use the dedicated Django client instead:

- **`useDjangoApi`** — same API as `useFetch`, with Django `baseURL` and CSRF headers on mutating requests (see [Custom useFetch](https://nuxt.com/docs/4.x/guide/recipes/custom-usefetch)).
- **`$djangoApi`** — imperative client from `useNuxtApp().$djangoApi` (used by `createDjangoModel` and related helpers).

```vue
<script setup lang="ts">
const { data: todos } = await useDjangoApi('/api/todos/')
</script>
```

```ts
const { $djangoApi } = useNuxtApp()
await $djangoApi('/api/todos/', { method: 'POST', body: { title: 'New' } })
```

## Development

Run these commands from `nuxt-django/`:

```bash
# Install dependencies
npm install

# Generate type stubs
npm run dev:prepare

# Develop with the playground
npm run dev

# Build the playground
npm run dev:build

# Run lint and tests
npm run lint
npm run test
```
