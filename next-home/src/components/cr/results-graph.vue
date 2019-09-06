<template>
    <div class="card mb-3">
        <div class="card-header">
            <h4>
                התפלגות ביטולים
            </h4>
        </div>
        <div class="card-body">
            <canvas class="main-chart"></canvas>
        </div>
    </div>
</template>

<script>
    import dtUtils from '../../lib/dt_utils';
    export default {
        props: ['reports'],
        mounted() {
            this.refresh();
        },
        methods: {
            refresh() {
                this.buildChart();
            },
            async buildChart() {
                let ctx = this.$el.querySelector('.main-chart');
                if (this.chart) {
                    this.chart.destroy();
                }
                let options = this.getOptions();
                let data = this.getData();
                this.chart = new Chart(ctx, {
                    type: 'bar',
                    data: data,
                    options: options,
                });

            },
            getUniqueReports() {
                let tripIdsSoFar = new Set();
                let result = [];
                for (let r of this.reports) {
                    if (!r.wrong_report && !tripIdsSoFar.has(r.gtfs_trip_id)) {
                        tripIdsSoFar.add(r.gtfs_trip_id);
                        result.push(r);
                    }
                }
                return result;
            },
            getByDayCounters(reports) {
                let counters = new Map();
                for (let r of reports) {
                    let dateStr = dtUtils.toIsoDateStr(r.created_at);
                    if (!counters.has(dateStr)) {
                        counters.set(dateStr, 1)
                    } else {
                        counters.set(dateStr, counters.get(dateStr) + 1);
                    }
                }
                let entries = [...counters.entries()]
                entries = _.sortBy(entries, e => e[0]);
                return entries.map(e => [dtUtils.dateStrToMidDay(e[0]), e[1]]);
            },
            getData() {
                let uniqueReports = this.getUniqueReports();
                console.log(`There are ${uniqueReports.length} unique valid from ${this.reports.length}`);
                let counters = this.getByDayCounters(uniqueReports);
                let timeData = counters.map(function(c) {
                    return {
                        x: c[0],
                        y: c[1],
                    }
                })
                return {
                    datasets: [
                        {
                            label: 'מספר ביטולים מדווחים ליום',
                            backgroundColor: '#ff0000',
                            data: timeData
                        }
                    ]
                }
            },
            getOptions() {
                return {
                    responsive: true,
                    maintainAspectRatio: false,
                    tooltips: {
                        callbacks: {
                            title: function(item, data) {
                                return dtUtils.toDate(item[0].xLabel);
                            },

                            label: function(item, data) {
                                return item.yLabel + ' ' + 'ביטולים';
                            }
                        }
                    },
                    scales: {
                        xAxes: [{
                            type: 'time',
                            time: {
                                unit: 'day'
                            },
                            ticks: {
                                callback: function (value, index, values) {
                                    let [m, d] = value.split(' ');
                                    let mi = dtUtils.engToNumber(m);
                                    if (mi) {
                                        return `${d} ${dtUtils.shortMonthNames[mi] }`
                                    }
                                    return value;
                                },
                            }
                        }],
                    },
                }
            }
        }
    }
</script>
