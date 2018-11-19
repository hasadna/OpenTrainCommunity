<template>
    <div class="card">
        <div class="card-header">
            {{ tripsCount }}
            נסיעות
            &bull;
            <month-year :month="begin[1]" :year="begin[0]"/>
            עד
            <month-year :month="config.end[1]" :year="config.end[0]"/>
            <button v-show="!loading" class="btn btn-outline-primary float-right" @click="editMode = !editMode">
                <i class="fa fa-pencil"></i>
            </button>
        </div>
        <div class="card-body">
            <div v-show="loading">
                <p class="text-center">
                    <i class="fa fa-spin fa-spinner fa-5x"></i>
                </p>
            </div>
            <div v-show="!editMode && !loading">
                <canvas class="main-chart"></canvas>
            </div>
            <div v-show="editMode && !loading">
                <form @submit="startNewSearch">
                    <div class="form-group">
                        <label>עד לחודש</label>
                        <select v-model="newSearch.ym" class="form-control">
                            <option v-for="ym in yms" :value="ym">
                                {{ ym[1] | monthName }} {{ ym[0] }}
                            </option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>מספר חודשים</label>
                        <input class="form-control" type="number" min="1" max="12" v-model="newSearch.months">
                    </div>
                     <button type="submit" class="btn btn-primary">
                         חשב מחדש
                     </button>
                </form>
            </div>
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
                loading: false,
                editMode: false,
                newSearch: {
                    ym: null,
                    months: 0,
                },
                chart: null,
                yms:[]
            }
        },
        mounted() {
            this.yms = this.$dtUtils.getRange(this.config.globalBegin, this.config.globalEnd);
            this.refresh();
        },
        computed: {
            tripsCount() {
                if (this.monthsData) {
                    return this._.sumBy(this.monthsData, t=>t.count);
                }
                return null;
            },
            begin() {
                return this.$dtUtils.computeStart(this.config.end, this.config.months);
            }
        },
        props: {
            config: Object
        },
        methods: {
            refresh() {
                this.buildChart();
                this.newSearch.ym = this.yms.find(ym => ym[0] == this.config.end[0] && ym[1] == this.config.end[1]);
               this.newSearch.months = this.config.months;
            },
            async startNewSearch(e) {
                this.loading = true;
                this.config.end = [...this.newSearch.ym];
                this.config.months = this.newSearch.months;
                this.editMode = false;
                this.refresh();
                e.preventDefault();
            },
            async buildChart() {
                let ctx = this.$el.querySelector('.main-chart');
                console.log(ctx);
                if (this.chart) {
                    this.chart.destroy();
                }
                this.tripData = await this.getData();
                let options = this.getOptions();
                this.chart = new Chart(ctx, {
                    type: 'horizontalBar',
                    data: this.tripData,
                    options: options,
                });
                this.loading = false;
            },
            async getData() {
                let resp = await this.$axios.get('/api/v1/monthly/', {
                    params: {
                        start_year: this.begin[0],
                        start_month: this.begin[1],
                        end_year: this.config.end[0],
                        end_month: this.config.end[1]
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