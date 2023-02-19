import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ViewTranscription from '../views/ViewTranscription.vue'

const routes = [
    {
        path: '/',
        name: 'home',
        component: Home
    },
    {
        path: '/viewTranscription/:id',
        name: 'viewTranscription',
        component: ViewTranscription
    },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
