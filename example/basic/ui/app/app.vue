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
    <UForm :state="newTodo" @submit="createTodo">
      <UFormField v-for="[key, field] in fields" :key="key" :name="key" :label="field.label" :type="field.type">
        <UInput v-model="newTodo[key]" :type="field.type" />
      </UFormField>
      <UButton
        label="Create"
        color="primary"
        variant="solid"
        :loading="creating"
        type="submit"
      />
    </UForm>
  </UApp>
</template>

<script setup>
const user = ref(window.django_nuxt.user)

const { data: todos, refresh } = await useDjangoModel('todo')
const { data: schema } = await useDjangoSchema('todo')

const newTodo = ref(Object.fromEntries(Object.entries(schema.value || {}).filter(([key, field]) => !key.startsWith('~') && !field.read_only).map(([key, field]) => [key, field.initial || null])))
const fields = Object.entries(schema.value || {}).filter(([key, field]) => !key.startsWith("~") && !field.read_only)

function createTodo(event) {
  createDjangoModel('todo', event.data).then(() => {
    refresh()
    newTodo.value = Object.fromEntries(Object.entries(schema.value || {}).filter(([key, field]) => !key.startsWith('~') && !field.read_only).map(([key, field]) => [key, field.initial || null]))
  })
}
</script>
