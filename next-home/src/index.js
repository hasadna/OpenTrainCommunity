import 'bootstrap';
import './style/bootstrap.rtl.css';
import './style/otrain.css';
import $ from 'jquery';
import axios from 'axios';
import _ from 'lodash';
import Vue from 'vue';
import TripsCharts from './components/trips-charts.vue';
import MonthYear from './components/month_year.vue';

$(function() {
    Vue.prototype.$axios = axios;
    Vue.prototype._ = _;

    Vue.filter('digits2', d => d < 10 ? '0' + d : '' + d);

    Vue.component('month-year', MonthYear);

    let app = new Vue({
        el: '#app',
        components: {
            'trips-charts': TripsCharts,
        }
    });
});
