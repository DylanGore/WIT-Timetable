import { createApp } from 'vue';

import App from './App.vue';
import router from './routes/main.routes';

import 'bootstrap';

const app = createApp(App);

app.use(router);

app.mount('#app');
