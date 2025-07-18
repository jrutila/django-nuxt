export default defineNuxtPlugin(() => {
  return {
    provide: {
      django_nuxt: (window as any).django_nuxt,
      has_perm: (permission: string): boolean => {
        const userPerms = (window as any).django_nuxt.perms || []
        return userPerms.includes(permission)
      },
      user: () => {
        return (window as any).django_nuxt.user || { is_authenticated: false }
      }
    }
  }
})
