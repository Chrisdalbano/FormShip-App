import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store/main'
import './assets/main.css'
import { useAxios } from '@/composables/useAxios';


const app = createApp(App)
useAxios();



app.use(router)
app.use(pinia)

app.mount('#app')
