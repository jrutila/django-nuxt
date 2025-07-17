import type { Ref } from "vue"
import { computed, ref } from "vue"
import { useFetch } from "nuxt/app"
import type { FetchError, FetchOptions } from 'ofetch'
import type { AsyncData, AsyncDataOptions, KeysOf, MultiWatchSources, PickFrom } from "nuxt/app"

type Pagination = {
  pageIndex: number
  pageSize: number
  total: number
}

type ReturnType = AsyncData<any[], FetchError> & { pagination: Ref<Pagination | undefined> }

export const useDjangoModel = async (model: string, query: Record<string, Ref<any>> = {}): Promise<ReturnType> => {
  const pagination = ref(undefined)
  const q = computed(() => {
    const b: Record<string, any> = {}
    let isSingle = false
    for (const [key, value] of Object.entries(query)) {
      if (key === "id") {
        isSingle = true
        continue
      }
      b[key] = value.value
    }
    if (pagination.value && pagination.value.pageIndex > 1) {
      b.page = pagination.value.pageIndex
    }
    return b
  })
  return { ...(await useFetch<any[]>(`/api/${model}/${query.id ? query.id.value + "/" : ''}`, {
    query: q,
    method: 'GET',
    transform: (data) => {
      if (data.count !== undefined) {
        if (!pagination.value && data.count > data.results.length) {
          pagination.value = {
            pageIndex: 1,
            pageSize: data.next ? data.results.length : 100
          }
        }
        if (data.count <= data.results.length) {
          pagination.value = undefined
        }
        if (pagination.value) {
        pagination.value.total = data.count
        }
        return data.results
      }
      return data
    }
  })), pagination }
}