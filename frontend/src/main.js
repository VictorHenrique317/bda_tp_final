import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import ChatDashboard from './components/ChatDashboard.vue'
import ChatUpload from './components/ChatUpload.vue'

const routes = [
  { path: '/', component: ChatUpload },
  { path: '/chat/:id', component: ChatDashboard, props: true }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')



