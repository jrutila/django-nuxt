import { ref } from "vue"

export const useDjangoNuxt = () => {
  return ref(window.django_nuxt)
}
