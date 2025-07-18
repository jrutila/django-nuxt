export const handDjangoServerErrors = (formRef: Ref<UFormRef>, schema: Ref<DjangoSchema> | DjangoSchema | null) => (error) => {
  const errors = JSON.parse(JSON.stringify(error?.data ?? error))
  for (const field of Object.keys(errors)) {
    if (!schema || field in (schema?.value || schema)) {
      for (const message of errors[field]) {
        formRef.value.errors.push({ name: field, message })
      }
      if (schema) {
        delete errors[field]
      }
    }
  }
  return errors
}
