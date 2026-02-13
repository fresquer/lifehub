import './theme.css'
import { applyThemeFromStorage } from './composables/useTheme'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

applyThemeFromStorage()
createApp(App).use(router).mount('#app')
