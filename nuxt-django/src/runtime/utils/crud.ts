import { useDjangoNuxtModelPath } from "../composables/useDjangoNuxtModelPath"
import { isRef } from "vue"
import type { Ref } from "vue"

export async function createDjangoModel(model: string, data: any, query: Record<string, Ref<any>> = {}) {
  let path: string | Ref<string | undefined> = useDjangoNuxtModelPath(model, data)
  if (isRef(path)) {
    path = path.value as string
  }
  return $fetch<any>(path, {
    method: 'POST',
    body: data,
    query: query,
  })
}

export async function updateDjangoModel(model: string, id: string, data: any, query: Record<string, Ref<any>> = {}) {
  const pathData = { ...data, id }
  let path: string | Ref<string | undefined> = useDjangoNuxtModelPath(model, pathData)
  if (isRef(path)) {
    path = path.value as string
  }
  return $fetch<any>(path, {
    method: 'PUT',
    body: data,
    query: query,
  })
}

export async function patchDjangoModel(model: string, id: string, data: any, query: Record<string, Ref<any>> = {}) {
  const pathData = { ...data, id }
  let path: string | Ref<string | undefined> = useDjangoNuxtModelPath(model, pathData)
  if (isRef(path)) {
    path = path.value as string
  }
  return $fetch<any>(path, {
    method: 'PATCH',
    body: data,
    query: query,
  })
}

export async function deleteDjangoModel(model: string, id: string, query: Record<string, Ref<any>> = {}) {
  const pathData = { id }
  let path: string | Ref<string | undefined> = useDjangoNuxtModelPath(model, pathData)
  if (isRef(path)) {
    path = path.value as string
  }
  return $fetch<any>(path, {
    method: 'DELETE',
    query: query,
  })
}
