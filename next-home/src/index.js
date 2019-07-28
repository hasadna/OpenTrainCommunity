import 'bootstrap';
import './style/bootstrap.rtl.css';
import './style/otrain.css';
import $ from 'jquery';
import axios from 'axios';
import _ from 'lodash';
import Vue from 'vue';
import VueRouter from 'vue-router';
import TripsCharts from './components/trips-charts.vue';
import CancelReports from './components/cancel-reports.vue';
import MonthYear from './components/month_year.vue';
import dtUtils from './lib/dt_utils';

function sleep(ms) {
    return new Promise((resolve, reject) => {
        window.setTimeout(() => resolve(true), ms);
    });
}

$(function() {
    let baseUrl = window.location.host.includes(":3000") ?
        'http://localhost:8000' :
        'https://otrain.org';
    console.log(`baseUrl = ${baseUrl}`);
    const axiosInstance = axios.create({
        baseURL: baseUrl,
    });
    Vue.prototype.$axios = axiosInstance;
    Vue.prototype._ = _;
    Vue.prototype.$sleep = sleep;
    Vue.prototype.$dtUtils = dtUtils;

    Vue.filter('digits2', d => d < 10 ? '0' + d : '' + d);
    Vue.filter('monthName', i => dtUtils.monthNames[i] || '???');
    Vue.filter('dayName', i => dtUtils.daysNames[i] || '???');
    Vue.filter('formatHours', hs => dtUtils.formatHours(hs));
    Vue.filter('to-date', d => dtUtils.toDate(d))
    Vue.filter('to-hm', d => dtUtils.toHM(d))
    Vue.filter('hms2hm', d => dtUtils.HMS2HM(d))
    Vue.config.errorHandler = function(err, vm, info) {
        console.error(err);
    };
    Vue.component('month-year', MonthYear);
    Vue.use(VueRouter);
    const routes = [
        {path: '/', component: TripsCharts},
        {path: '/reports', component: CancelReports},
        { path: '*', redirect: '/' }
    ];

    const router = new VueRouter({
        routes
    });

    let app = new Vue({
        router: router,
        el: '#app',
        data: {
            appTitle: 'מדד האיחור שלנו',
        },
        methods: {
            setTitle(t) {
                this.appTitle = t;
            },
            restoreTitle() {
                this.appTitle = 'מדד האיחור שלנו';
            }
        }
    });
});
