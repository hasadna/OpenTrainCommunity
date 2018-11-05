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
    let resp = await axios.get('https://otrain.org/api/v1/monthly/', {
        params: {
            start_year: 2018,
            start_month: 1,
            end_year: 2018,
            end_month: 5
        }
    });
    let months = resp.data;
    let labels = months.map(m=>`${m.m}/${m.y}`);
    let data = months.map(m=>Math.floor(100*m.is_late/m.count));
    console.log(labels.length);
    console.log(data.length);
    return {
        labels: labels,
        datasets: [{
            label: '% of late trips',
            data: data,
            borderWidth: 1,
            backgroundColor: 'red'
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
