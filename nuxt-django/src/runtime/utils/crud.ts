export async function createDjangoModel(model: string, data: any, query: Record<string, Ref<any>> = {}) {
  return $fetch<any>(`/api/${model}/`, {
    method: 'POST',
    body: data,
    query: query,
  })
}

export async function updateDjangoModel(model: string, id: string, data: any, query: Record<string, Ref<any>> = {}) {
  return $fetch<any>(`/api/${model}/${id}/`, {
    method: 'PUT',
    body: data,
    query: query,
  })
}

export async function patchDjangoModel(model: string, id: string, data: any, query: Record<string, Ref<any>> = {}) {
  return $fetch<any>(`/api/${model}/${id}/`, {
    method: 'PATCH',
    body: data,
    query: query,
  })
}

export async function deleteDjangoModel(model: string, id: string, query: Record<string, Ref<any>> = {}) {
  return $fetch<any>(`/api/${model}/${id}/`, {
    method: 'DELETE',
    query: query,
  })
}
