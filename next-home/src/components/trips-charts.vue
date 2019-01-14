<template lang="html">
    <div>
        <div class="row">
            <div class="col-12">
                <div class="alert alert-info">
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                    <div>
                        <h2 style="display: inline-block">
                        <span style="color: orange">
                            <i class="fas fa-rectangle-wide"></i>
                        </span>
                            מדד איחור רכבת ישראל
                        </h2>
                        &nbsp;&nbsp;
                        מתייחס לרכבת כמאחרת אם היא איחרה
                        <b>
                        לתחנת היעד שלה
                        </b>
                        ב 5 דקות או יותר
                    </div>
                    <div>
                        <h2 style="display: inline-block">
                        <span style="color: red">
                            <i class="fas fa-rectangle-wide"></i>
                        </span>
                            מדד איחור אלטרנטיבי</h2>
                        &nbsp;&nbsp;
                        מתייחס לרכבת כמאחרת אם היא איחרה
                        <b>
                        לתחנה כלשהי
                            </b>
                        לאורך המסלול ב 5 דקות או יותר

                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6 col-12" :class="{'offset-sm-3': configs.length == 1 }"
                 v-for="config in configs">
                <trips-chart :global="global" :config="config" @remove="remove(config)" @editDone="refreshUrl()"/>
            </div>
        </div>
        <div class="row mt-5">
            <div class="col-sm-6 col-12 offset-sm-3">
                <button class="btn btn-outline-primary btn-block" @click="addNew">
                    הוסף תרשים חדש
                </button>
            </div>
        </div>
    </div>
</template>

<script>
    import TripsChart from './trips-chart.vue';

    export default {
        components: {
            'trips-chart': TripsChart
        },
        data() {
            return {
                configs: [],
                global: {
                    begin: null,
                    end: null
                }
            }
        },
        async created() {
            window.tc = this;
            await this.getGlobalData();
            let configs = this.getConfigsFromUrl();
            if (!configs) {
                configs = [{
                    e: [...this.global.end],
                    m: 5,
                }]
            }
            this.configs = configs.map(c => this.fromDump(c));
            this.refreshUrl();
        },
        methods: {
            async getGlobalData() {
                let buildDates = async () => {
                    let resp = await this.$axios.get("/api/v1/monthly/year-months/");
                    this.global.begin = resp.data.first;
                    this.global.end = resp.data.last;
                };
                let buildStops = async () => {
                    let resp = await this.$axios.get("/api/v1/stops/");
                    this.global.stops = this._.sortBy(resp.data, s => s.name);
                };
                await buildDates();
                await buildStops();
            },
            stopFromId(stopId) {
                if (!stopId) {
                    return null;
                }
                return this.global.stops.find(s => s.id == stopId);
            },
            getConfigsFromUrl() {
                let search = window.location.search;
                if (!search) {
                    return null;
                }
                let pat = /^[\?]?charts=(.*)$/;
                let result = search.match(pat);
                if (!result) {
                    return null;
                }
                try {
                    return JSON.parse(decodeURIComponent(result[1]));
                } catch (err) {
                    console.error(err);
                    return null;
                }
            },
            remove(config) {
                this.configs = this.configs.filter(c => c != config);
                this.refreshUrl();
            },
            addNew() {
                this.configs.push({
                    end: [...this.global.end],
                    months: 5,
                    stop1: null,
                    stop2: null,
                    days: null,
                });
                this.refreshUrl();
            },
            refreshUrl() {
                let dumps = this.configs.map(c => this.dumpConfig(c));
                let params = JSON.stringify(dumps);
                window.history.pushState(null, null, `?charts=${params}`);
            },
            dumpConfig(config) {
                let result = {
                    e: config.end,
                    m: config.months,
                };
                if (config.stop1) {
                    result.s1 = config.stop1.id;
                };
                if (config.stop2) {
                    result.s2 = config.stop2.id;
                };
                if (config.days && config.days.length) {
                    result.d = config.days;
                };
                if (config.hours && config.hours.length) {
                    result.h = config.hours;
                }
                return result;
            },
            fromDump(c) {
                return {
                    end: c.e,
                    months: c.m,
                    stop1: this.stopFromId(c.s1),
                    stop2: this.stopFromId(c.s2),
                    days: c.d || [],
                    hours: c.h || [],
                }
            }
        }
    }
</script>