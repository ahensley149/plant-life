import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import VueApexCharts from 'vue-apexcharts';
import VueFlip from 'vue-flip';
import App from './App.vue';
import router from './router';
import 'bootstrap/dist/css/bootstrap.css';

Vue.use(BootstrapVue);
Vue.use(VueApexCharts);
Vue.use(VueFlip);

Vue.config.productionTip = false;

new Vue({
  router,
  render: (h) => h(App),
}).$mount('#app');
