<template>
  <div>
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
  </div>
</template>

<script setup>
const user = ref(window.django_nuxt.user)

const { data: todos, refresh } = await useDjangoModel('todos')
</script>
