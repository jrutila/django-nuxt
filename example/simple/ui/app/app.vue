<template>
  <div>
    <NuxtRouteAnnouncer />
    <div>
      Hello {{ user.username }}
    </div>
  </div>
</template>

<script setup>
const user = ref(window.django_nuxt.user)
</script>
