import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import UsuarioLayout from '../views/UsuarioLayout.vue'
import Usuario from '../views/Usuario.vue'
import Configuracion from '../views/Configuracion.vue'
import Areas from '../views/Areas.vue'
import ConfiguracionAreas from '../views/ConfiguracionAreas.vue'
import Tareas from '../views/Tareas.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/signup', name: 'Register', component: Register },
  {
    path: '/dashboard',
    component: UsuarioLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: Areas, meta: { pageTitle: 'Áreas y proyectos' } },
      { path: 'tareas', name: 'Tareas', component: Tareas, meta: { pageTitle: 'Tareas' } },
      { path: 'usuario', name: 'Usuario', component: Usuario, meta: { pageTitle: 'Mi perfil' } },
      { path: 'usuario/configuracion', name: 'Configuracion', component: Configuracion, meta: { pageTitle: 'Configuración' } },
      { path: 'configuracion-areas', name: 'ConfiguracionAreas', component: ConfiguracionAreas, meta: { pageTitle: 'Configuración áreas' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, _from, next) => {
  const auth = useAuth()
  const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)
  if (requiresAuth) {
    if (!auth.token.value) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    await auth.fetchUser()
    if (!auth.token.value) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    next()
  } else {
    next()
  }
})

export default router
