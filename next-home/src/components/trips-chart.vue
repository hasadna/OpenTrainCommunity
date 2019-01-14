<template>
    <div class="card">
        <div class="card-header">
            {{ tripsCount }}
            נסיעות
            &bull;
            <month-year :month="begin[1]" :year="begin[0]"/>
            עד
            <month-year :month="config.end[1]" :year="config.end[0]"/>
            <span v-if="config.stop1 && config.stop2">
                &bull;
                דרך
                {{ config.stop1.name }}
                ו
                {{ config.stop2.name }}
            </span>
            <span v-else-if="config.stop1">
                &bull;
                דרך
                {{ config.stop1.name }}
            </span>
            <span v-if="config.days && config.days.length">
                &bull;
                <span v-if="config.days.length > 1">
                בימים
                </span>
                <span v-else>
                    ביום
                </span>
                <span v-for="day in _.sortBy(config.days)">
                    {{ day | dayName }}
                </span>
            </span>
            <span v-if="config.hours && config.hours.length">
                &bull;
                <span>בשעות</span>
                {{ config.hours | formatHours }}
            </span>
            <div class="float-right">
                <button v-show="!loading" class="btn btn-outline-primary" @click="editMode = !editMode">
                    <i :class="{'fal fa-pencil': !editMode, 'fal fa-chart-bar': editMode}">
                    </i>
                </button>
                <button v-show="!loading" class="btn btn-outline-danger" @click="$emit('remove', config)">
                    <i class="fa fa-trash"></i>
                </button>
            </div>
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
                    <div class="form-group row">
                        <label class="col-2">עד לחודש</label>
                        <div class="col-10">
                            <select v-model="newSearch.end" class="form-control">
                                <option v-for="ym in yms" :value="ym">
                                    {{ ym[1] | monthName }} {{ ym[0] }}
                                </option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group row">
                        <label class="col-2">מספר חודשים</label>
                        <div class="col-10">
                            <input class="form-control" type="number" min="1" max="36" v-model="newSearch.months">
                        </div>
                    </div>
                    <div class="form-group row">
                        <label class="col-2">עובר דרך תחנה</label>
                        <div class="col-10">
                            <select class="form-control" v-model="newSearch.stop1" >
                                <option value="">------------</option>
                                <option v-for="stop in global.stops" :value="stop" >{{ stop.name }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group row">
                        <label class="col-2">ואז דרך תחנה</label>
                        <div class="col-10">
                            <select class="form-control" v-model="newSearch.stop2" >
                                <option value="">------------</option>
                                <option v-for="stop in global.stops" :value="stop" >{{ stop.name }}</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group row">
                        <label class="col-2">ימים בשבוע</label>
                        <div class="col-10">
                            <div class="form-check form-check-inline" v-for="day in [0,1,2,3,4,5,6]">
                              <input class="form-check-input" type="checkbox" :value=day v-model="newSearch.days">
                              <label class="form-check-label">{{ day | dayName }}</label>
                            </div>
                        </div>
                    </div>
                    <div class="form-group row">
                        <label class="col-2">שעת יציאה</label>
                        <div class="col-10">
                            <div class="form-check form-check-inline" v-for="hour in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]">
                              <input class="form-check-input" type="checkbox" :value=hour v-model="newSearch.hours">
                              <label class="form-check-label">{{ hour }}</label>
                            </div>
                        </div>
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
    import dtUtils from '../lib/dt_utils';
    export default {
        data() {
            return {
                tripData: null,
                monthsData: null,
                loading: false,
                editMode: false,
                newSearch: {
                    end: null,
                    months: 0,
                    stop1: null,
                    stop2: null,
                    days: [],
                    hours: [],
                },
                chart: null,
                yms:[]
            }
        },
        mounted() {
            this.yms = this.$dtUtils.getRange(this.global.begin, this.global.end);
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
            config: Object,
            global: Object,
        },
        methods: {
            refresh() {
                this.buildChart();
                this.newSearch.end = this.yms.find(ym => ym[0] == this.config.end[0] && ym[1] == this.config.end[1]);
               this.newSearch.months = this.config.months;
               this.newSearch.stop1 = this.config.stop1;
               this.newSearch.stop2 = this.config.stop2;
               this.newSearch.days = this.config.days;
               this.newSearch.hours = this.config.hours;
            },
            async startNewSearch(e) {
                this.loading = true;
                this.config.end = [...this.newSearch.end];
                this.config.months = this.newSearch.months;
                this.config.stop1 = this.newSearch.stop1;
                this.config.stop2 = this.newSearch.stop2;
                this.config.days = this.newSearch.days;
                this.config.hours = this.newSearch.hours;
                // make sure that if there is only 1 it
                // will be stop1
                if (this.config.stop2 && !this.config.stop1) {
                    this.config.stop1 = this.config.stop2;
                    this.config.stop2 = null;
                }
                this.editMode = false;
                this.$emit("editDone");
                this.refresh();
                e.preventDefault();
            },
            async buildChart() {
                let ctx = this.$el.querySelector('.main-chart');
                if (this.chart) {
                    this.chart.destroy();
                }
                let respData = await this.getRespDataFromServer();
                let data = this.getData(respData);
                let options = this.getOptions(respData);
                this.chart = new Chart(ctx, {
                    type: 'horizontalBar',
                    data: data,
                    options: options,
                });
                this.loading = false;
            },
            async getRespDataFromServer() {
                let params = {
                    start_year: this.begin[0],
                    start_month: this.begin[1],
                    end_year: this.config.end[0],
                    end_month: this.config.end[1],
                };
                if (this.config.stop1) {
                    params.stop1 = this.config.stop1.id;
                }
                if (this.config.stop2) {
                    params.stop2 = this.config.stop2.id;
                }
                if (this.config.days && this.config.days.length > 0 && !dtUtils.isFullWeek(this.config.days)) {
                    params.days = this.config.days.join(",")
                }
                if (this.config.hours && this.config.hours.length > 0) {
                    params.hours = this.config.hours.join(",")
                }
                let resp = await this.$axios.get('/api/v1/monthly/', {
                    params: params
                });
                return resp.data;
            },
            getData(respData) {
                this.monthsData = respData;
                let months = this.monthsData;
                let labels = months.map(m => `${m.m}/${m.y}`);
                let dataMax = months.map(m => Math.floor(100 * m.count_late_max / m.count));
                let dataLast = months.map(m => Math.floor(100 * m.count_late_last / m.count));
                return {
                    labels: labels,
                    datasets: [{
                        label: 'מדד איחור אלטרנטיבי',
                        data: dataMax,
                        borderWidth: 1,
                        backgroundColor: 'red'
                    }, {
                        label: 'מדד איחור רכבת ישראל',
                        data: dataLast,
                        borderWidth: 1,
                        backgroundColor: 'orange'
                    }]
                }
            },
            getOptions(respData) {
                let months = respData;
                let fullLabels = months.map(m => `${dtUtils.monthNames[m.m]} ${m.y}`);
                return {
                    responsive: true,
                    maintainAspectRatio: false,
                    tooltips: {
                        callbacks: {
                            title: function(item, data) {
                                // Pick first xLabel for now
                                let title = fullLabels[item[0].index];
                                let count = months[item[0].index].count;
                                let t = 'נסיעות';
                                return `${title} - ${count} ${t}`;
                            },

                            label: function(item, data) {
                                let datasetLabel = data.datasets[item.datasetIndex].label || '';
                                return datasetLabel + ': ' + item.xLabel + '%';
                            }
                        }
                    },
                    scales: {
                        xAxes: [{
                            ticks: {
                                beginAtZero: true,
                                callback: function(value, index, values) {
                                        return value + '%';
                                },
                            },
                            scaleLabel: {
                                display: true,
                                labelString: 'אחוז רכבות מאחרות'
                            }
                        }],
                        yAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'חודש',
                            }
                        }]
                    },
                }
            }

        }
    }
</script>