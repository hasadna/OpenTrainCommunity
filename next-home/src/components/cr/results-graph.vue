<template>
    <div class="card mb-3">
        <div class="card-header">
            <h4>
                התפלגות ביטולים
                <div class="btn btn-group float-right">
                    <button v-for="freq in freqs"
                            class="btn"
                            :class="{'btn-outline-primary': curFreq !== freq, 'btn-primary disabled pointer-events-none': curFreq === freq}"
                            @click="curFreq = freq ; refresh()"
                    >
                        {{ freq.title }}
                    </button>
                </div>
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
        data() {
            return {
                freqs: [
                    {
                        title: 'יומי',
                        code: 'd',
                        unit: 'day',
                        tickName(m, d) {
                            let mi = dtUtils.engToNumber(m);
                            if (mi) {
                                return `${d} ${dtUtils.shortMonthNames[mi] }`
                            }
                        },
                        barTitle(dt) {
                            return dtUtils.toDate(dt);
                        }
                    },
                    {
                        title: 'שבועי',
                        code: 'w',
                        unit: 'week',
                        tickName(m, d) {
                            let mi = dtUtils.engToNumber(m);
                            if (mi) {
                                let prefix = 'שבוע מ ';
                                return `${prefix} ${d} ${dtUtils.shortMonthNames[mi] }`
                            }
                        },
                        barTitle(dt) {
                            let sunday = dt;
                            let saturday = new Date(dt);
                            saturday.setDate(dt.getDate() + 6);
                            if (sunday.getDay() != 0) {
                                console.error('error in sunday');
                            }
                            if (saturday.getDay() != 6) {
                                console.error('error in saturday');
                            }
                            let t1 =  'ראשון' + ' ' + dtUtils.toDate(sunday)
                            let t2 = 'שבת' + ' ' + dtUtils.toDate(saturday);
                            return `${t1} - ${t2}`;
                        },

                    },
                    {
                        title: 'חודשי',
                        code: 'm',
                        unit: 'month',
                        tickName(m, d) {
                            let mi = dtUtils.engToNumber(m);
                            if (mi) {
                                return `${dtUtils.shortMonthNames[mi] }`
                            }
                        },
                        barTitle(dt) {
                            let m = dt.getMonth() + 1;
                            return 'חודש ' + dtUtils.monthNames[m];
                        }
                    }
                ],
                curFreq: null
            }
        },
        props: ['unique-reports'],
        created() {
            this.curFreq = this.freqs[0];
        },
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
            getByFreqCounters(reports) {
                let counters = new Map();
                for (let r of reports) {
                    let dateStr = dtUtils.toFreqStr(r.created_at, this.curFreq.code);
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
                let counters = this.getByFreqCounters(this.uniqueReports);
                let timeData = counters.map(function(c) {
                    return {
                        x: c[0],
                        y: c[1],
                    }
                })
                return {
                    datasets: [
                        {
                            label: 'מספר ביטולים מדווחים' + ' ' + this.curFreq.title,
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
                            title: (item, data) => {
                                return this.curFreq.barTitle(new Date(item[0].xLabel));
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
                                unit: this.curFreq.unit
                            },
                            ticks: {
                                beginAtZero: true,
                                callback: (value, index, values) => {
                                    let [m, d] = value.split(' ');
                                    return this.curFreq.tickName(m, d) || value;
                                },
                            }
                        }],
                    },
                }
            }
        }
    }
</script>
