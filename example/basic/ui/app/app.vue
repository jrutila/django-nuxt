<template>
  <UApp>
    <NuxtRouteAnnouncer />
    <div>
      Hello {{ user.username }}
    </div>
    <div>
      <ul>
        <li v-for="todo in todos" :key="todo.id">{{ todo.title }}</li>
      </ul>
    </div>
    <div>
      <UButton @click="refresh">Refresh</UButton>
    </div>

    <h2>Add another todo</h2>
    <UForm ref="todoForm" v-if="$has_perm('todo_app.add_todo')" :schema="schema" :state="newTodo" @submit="createTodo">
      <UAlert v-for="error in non_field_errors" :key="error" color="error" variant="subtle" :title="error" />
      <UFormField v-for="[key, field] in fields" :key="key" :name="key" :label="field.label" :type="field.type">
        <UInput v-model="newTodo[key]" :type="field.type" />
      </UFormField>
      <UButton
        label="Create"
        color="primary"
        variant="solid"
        type="submit"
      />
    </UForm>
    <div v-else>
      You don't have permission to add todos
    </div>
  </UApp>
</template>

<script setup>
const user = ref(window.django_nuxt.user)

const { data: todos, refresh } = await useDjangoModel('todo')
const { data: schema } = await useDjangoSchema('todo')

const todoForm = useTemplateRef('todoForm')
const newTodo = ref(Object.fromEntries(Object.entries(schema.value || {}).filter(([key, field]) => !key.startsWith('~') && !field.read_only).map(([key, field]) => [key, field.initial || null])))
const fields = Object.entries(schema.value || {}).filter(([key, field]) => !key.startsWith("~") && !field.read_only)
const non_field_errors = ref([])

function createTodo(event) {
  non_field_errors.value = []
  createDjangoModel('todo', event.data).then(() => {
    refresh()
    // reset form
    newTodo.value = Object.fromEntries(Object.entries(schema.value || {}).filter(([key, field]) => !key.startsWith('~') && !field.read_only).map(([key, field]) => [key, field.initial || null]))
  }).catch(e => {
    const excess_errors = handDjangoServerErrors(todoForm, schema)(e)
    non_field_errors.value = excess_errors['non_field_errors'] || []
  })
}
</script>
