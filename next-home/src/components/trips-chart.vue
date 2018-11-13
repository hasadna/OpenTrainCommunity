<template>
<div class="card">
    <div class="card-header">
        {{ tripsCount }}
        נסיעות
        &bull;
        <month-year :month="config.startMonth" :year="config.startYear"/>
        עד
        <month-year :month="config.endMonth" :year="config.endYear"/>
    </div>
    <div class="card-body">
        <p class="text-center" v-if="loading">
            <i class="fa fa-spin fa-spinner fa-5x"></i>
        </p>
        <canvas id="main-chart"></canvas>
    </div>
</div>
</template>

<script>
    import Chart from 'chart.js';
    export default {
        data() {
            return {
                tripData: null,
                monthsData: null,
                loading: true,
            }
        },
        mounted() {
            this.buildChart();
        },
        computed: {
            tripsCount() {
                if (this.monthsData) {
                    return this._.sumBy(this.monthsData, t=>t.count);
                }
                return null;
            }
        },
        props: {
            config: Object
        },
        methods: {
            async buildChart() {
                let ctx = document.getElementById('main-chart');
                this.tripData = await this.getData();
                let options = this.getOptions();
                this.loading = false;
                let chart = new Chart(ctx, {
                    type: 'horizontalBar',
                    data: this.tripData,
                    options: options,
                });
            },
            async getData() {
                let resp = await this.$axios.get('/api/v1/monthly/', {
                    params: {
                        start_year: this.config.startYear,
                        start_month: this.config.startMonth,
                        end_year: this.config.endYear,
                        end_month: this.config.endMonth
                    }
                });
                this.monthsData = resp.data;
                let months = resp.data;
                let labels = months.map(m => `${m.m}/${m.y}`);
                let dataMax = months.map(m => Math.floor(100 * m.count_late_max / m.count));
                let dataLast = months.map(m => Math.floor(100 * m.count_late_last / m.count));
                return {
                    labels: labels,
                    datasets: [{
                        label: 'אחוז נסיעות מאחרות לפי איחור מקסימלי',
                        data: dataMax,
                        borderWidth: 1,
                        backgroundColor: 'red'
                    }, {
                        label: 'אחוז נסיעות מאחרות לפי איחור ביעד',
                        data: dataLast,
                        borderWidth: 1,
                        backgroundColor: 'orange'
                    }]
                }
            },
            getOptions() {
                return {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        xAxes: [{
                            ticks: {
                                beginAtZero: true,
                            }
                        }]
                    }
                }
            }

        }
    }
</script>