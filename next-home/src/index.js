import 'bootstrap';
import './style/bootstrap.rtl.css';
import './style/otrain.css';
import $ from 'jquery';
import axios from 'axios';
import _ from 'lodash';
import Vue from 'vue';
import TripsCharts from './components/trips-charts.vue';
import MonthYear from './components/month_year.vue';

function sleep(ms) {
    return new Promise((resolve, reject) => {
        window.setTimeout(() => resolve(true), ms);
    });
}

$(function() {
    const axiosInstance = axios.create({
      baseURL: 'http://otrain.org',
    });

    Vue.prototype.$axios = axiosInstance;
    Vue.prototype._ = _;
    Vue.prototype.$sleep = sleep;

    Vue.filter('digits2', d => d < 10 ? '0' + d : '' + d);

    Vue.component('month-year', MonthYear);

    let app = new Vue({
        el: '#app',
        components: {
            'trips-charts': TripsCharts,
        }
    });
});
