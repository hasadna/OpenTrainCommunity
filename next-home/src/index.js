import 'bootstrap';
import './style/bootstrap.rtl.css';
import './style/otrain.css';
import $ from 'jquery';
import axios from 'axios';
import _ from 'lodash';
import Vue from 'vue';
import TripsCharts from './components/trips-charts.vue';
import MonthYear from './components/month_year.vue';
import dtUtils from './lib/dt_utils';

function sleep(ms) {
    return new Promise((resolve, reject) => {
        window.setTimeout(() => resolve(true), ms);
    });
}

$(function() {
    const axiosInstance = axios.create({
        baseURL: 'https://otrain.org',
        //baseURL: 'http://localhost:8000',
    });

    Vue.prototype.$axios = axiosInstance;
    Vue.prototype._ = _;
    Vue.prototype.$sleep = sleep;
    Vue.prototype.$dtUtils = dtUtils;

    Vue.filter('digits2', d => d < 10 ? '0' + d : '' + d);
    Vue.filter('monthName', i => dtUtils.monthNames[i] || '???');
    Vue.filter('dayName', i => dtUtils.daysNames[i] || '???');
    Vue.filter('formatHours', hs => dtUtils.formatHours(hs));
    Vue.config.errorHandler = function(err, vm, info) {
        console.error(err);
    }
    Vue.component('month-year', MonthYear);

    let app = new Vue({
        el: '#app',
        components: {
            'trips-charts': TripsCharts,
        }
    });
});
