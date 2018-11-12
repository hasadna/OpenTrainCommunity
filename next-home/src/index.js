import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './style/otrain.css';
import Chart from 'chart.js';
import $ from 'jquery';
import axios from 'axios';
import colors from './colors';


async function buildChart() {
    let ctx = document.getElementById('main-chart');
    let data = await getData();
    let options = getOptions();
    let chart = new Chart(ctx, {
        type: 'horizontalBar',
        data: data,
        options: options,
    });
}

async function getData() {
    let resp = await axios.get('http://localhost:8000/api/v1/monthly/', {
        params: {
            start_year: 2018,
            start_month: 1,
            end_year: 2018,
            end_month: 5
        }
    });
    let months = resp.data;
    let labels = months.map(m=>`${m.m}/${m.y}`);
    let dataMax = months.map(m=>Math.floor(100*m.count_late_max/m.count));
    let dataLast = months.map(m=>Math.floor(100*m.count_late_last/m.count));
    console.log(labels.length);
    return {
        labels: labels,
        datasets: [{
            label: '% of late trips (max)',
            data: dataMax,
            borderWidth: 1,
            backgroundColor: 'red'
        }, {
            label: '% of late trips (last)',
            data: dataLast,
            borderWidth: 1,
            backgroundColor: 'orange'
        }]
    }
}

function getOptions() {
    return {
        maintainAspectRatio: false,
        scales: {
            xAxes: [{
                ticks: {
                    beginAtZero: true,
                }
            }]
        }
    }
}

$(function() {
    buildChart();
});
