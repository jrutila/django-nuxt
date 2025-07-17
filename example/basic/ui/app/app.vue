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
      <button @click="refresh">Refresh</button>
    </div>
    {{ schema }}
    <UForm :schema="schema" v-model="newTodo">
      <UFormField v-for="field in fields" :key="field[0]" :name="field[0]" :label="field[1].label" :type="field[1].type">
        <UInput v-model="newTodo[field[0]]" />
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

const newTodo = ref({})
const fields = Object.entries(schema.value || {}).filter(([key, field]) => !key.startsWith("~") && !field.read_only)
</script>
