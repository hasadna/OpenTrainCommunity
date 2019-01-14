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
            <div class="col-12">
                <h1 class="text-center">{{ title }}
                    <div class="float-left">
                        <button class="btn btn-outline-primary" title="קישור לשיתוף" @click="share" :disabled="sharedDisabled">
                            <i class="fas fa-share-alt"></i>
                        </button>
                        <div class="alert alert-danger d-inline-block" style="font-size: 16px" v-if="shareError">
                            <small>
                            השמירה נכשלה
                                </small>
                        </div>
                        <div class="alert alert-success d-inline-block" style="font-size: 16px" v-if="shareUrl">
                            קישור
                            <code>{{shareUrl}}</code>
                        </div>
                    </div>
                </h1>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-6 col-12" :class="{'offset-sm-3': configs.length == 1 }"
                 v-for="config in configs">
                <trips-chart :global="global" :config="config" @remove="remove(config)"/>
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
                shareError: null,
                sharedDisabled: false,
                shareUrl: null,
                id: null,
                global: {
                    begin: null,
                    end: null
                },
                title: 'תרשים חדש',
            }
        },
        async mounted() {
            window.ts = this;
            await this.getGlobalData();
            let isRestored = false;
            try {
                isRestored = await this.restoreSharedData();
            } catch(err) {
                console.error(err);
                this.id = null;
                this.refreshUrl();
            }
            if (!isRestored) {
                this.configs = [{
                    end: [...this.global.end],
                    months: 5,
                }];
            }
        },
        methods: {
            async restoreSharedData() {
                let id = this.getIdFromUrl();
                if (!id) {
                    return false;
                }
                let resp = await this.$axios.get(`/api/v1/stories/${id}`);
                let dump = resp.data.dump;
                this.title = dump.title || this.title;
                this.configs = dump.configs;
                return true;
            },
            getIdFromUrl() {
                let s = window.location.search;
                if (!s) {
                    return null;;
                }
                if (!s.startsWith('?id=')) {
                    return null;
                }
                let id = s.substr(4);
                return id;
            },
            async reset() {
                this.id = null;
                this.configs = [];
                this.refreshUrl();
            },
            async share() {
                try {
                    this.shareError = false;
                    this.sharedDisabled = true;
                    this.shareUrl = null;
                    window.setTimeout(() => {
                        this.sharedDisabled = false;
                    }, 500);
                    let url = "/api/v1/stories/share/";
                    let resp = await this.$axios.post(url, {
                        dump: {
                            configs: this.configs,
                            title: this.title,
                        }
                    });
                    this.id = resp.data.id;
                    this.refreshUrl();
                    this.shareUrl = window.location.href;
                } catch (err) {
                    console.error(err);
                    this.shareError = err;
                }
            },
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
            // getConfigsFromUrl() {
            //     let search = window.location.search;
            //     if (!search) {
            //         return null;
            //     }
            //     let pat = /^[\?]?charts=(.*)$/;
            //     let result = search.match(pat);
            //     if (!result) {
            //         return null;
            //     }
            //     try {
            //         return JSON.parse(decodeURIComponent(result[1]));
            //     } catch (err) {
            //         console.error(err);
            //         return null;
            //     }
            // },
            remove(config) {
                this.configs = this.configs.filter(c => c != config);
            },
            addNew() {
                this.configs.push({
                    end: [...this.global.end],
                    months: 5,
                    stop1: null,
                    stop2: null,
                    days: null,
                });
            },
            refreshUrl() {
                window.history.pushState(null, null, this.id ? `?id=${this.id}` : '/');
            },
        }
    }
</script>