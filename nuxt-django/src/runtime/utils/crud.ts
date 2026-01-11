import { useDjangoNuxtModelPath } from "../composables/useDjangoNuxtModelPath"

export async function createDjangoModel(model: string, data: any, query: Record<string, Ref<any>> = {}) {
  const path = useDjangoNuxtModelPath(model, data)
  return $fetch<any>(path, {
    method: 'POST',
    body: data,
    query: query,
  })
}

export async function updateDjangoModel(model: string, id: string, data: any, query: Record<string, Ref<any>> = {}) {
  const pathData = { ...data, id }
  const path = useDjangoNuxtModelPath(model, pathData)
  return $fetch<any>(path, {
    method: 'PUT',
    body: data,
    query: query,
  })
}

export async function patchDjangoModel(model: string, id: string, data: any, query: Record<string, Ref<any>> = {}) {
  const pathData = { ...data, id }
  const path = useDjangoNuxtModelPath(model, pathData)
  return $fetch<any>(path, {
    method: 'PATCH',
    body: data,
    query: query,
  })
}

export async function deleteDjangoModel(model: string, id: string, query: Record<string, Ref<any>> = {}) {
  const pathData = { id }
  const path = useDjangoNuxtModelPath(model, pathData)
  return $fetch<any>(path, {
    method: 'DELETE',
    query: query,
  })
}
