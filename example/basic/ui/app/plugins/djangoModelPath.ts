export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.provide('djangoNuxtModelPath', (model: string, idOrQuery: string | any | null = null) => {

    let id = null
    if (idOrQuery) {
      if (typeof idOrQuery === 'object') {
        id = idOrQuery.id
      } else {
        id = idOrQuery
      }
    }
    if (model === 'whos') {
      console.log('whos', idOrQuery)
      const pk = isRef(idOrQuery.pk) ? idOrQuery.pk.value : idOrQuery.pk
      return `/api/todo/${pk}/whos`
    }
    return `/api/${model}/${id ? `${id}/` : ''}`
  })
})