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
  },
})
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
