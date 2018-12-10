<template lang="html">
    <div>
        <div class="row">
            <div class="col-12">
                <div class="alert alert-info">
                    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                    <p>
                        התרשימים מציגים את אחוז הרכבות המאחרות בחתך של חודשים. רכבת נחשבת מאחרת אם היא איחרה ב 5 דקות או
                        יותר.
                    </p>
                    <p>
                        ישנם שני מדדים לאיחור - הראשון הוא לפי האיחור המקסימלי לאורך המסלול, והשני הוא לפי האיחור בתחנה
                        האחרונה (תחנת היעד)
                    </p>
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
            await this.getGlobalData();
            let configs = this.getConfigsFromUrl();
            if (!configs) {
                configs = [{
                        e: [...this.global.end],
                        m: 5,
                    }]
            }
            this.configs = configs.map(c=>this.fromDump(c));
            this.refreshUrl();
        },
        methods: {
            async getGlobalData() {
                let resp = await this.$axios.get("/api/v1/monthly/year-months/");
                this.global.begin = resp.data.first;
                this.global.end = resp.data.last;
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
                this.configs = this.configs.filter(c=>c!=config);
                this.refreshUrl();
            },
            addNew() {
                this.configs.push({
                    end: [...this.global.end],
                    months: 5,
                });
                this.refreshUrl();
            },
            refreshUrl() {
                let dumps = this.configs.map(c=>this.dumpConfig(c));
                let params = JSON.stringify(dumps);
                window.history.pushState(null, null, `?charts=${params}`);
            },
            dumpConfig(config) {
                return {
                    e: config.end,
                    m: config.months,
                }
            },
            fromDump(c) {
                return {
                    end: c.e,
                    months: c.m,
                }
            }
        }
    }
</script>