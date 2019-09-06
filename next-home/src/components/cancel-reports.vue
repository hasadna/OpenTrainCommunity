<template lang="html">
    <div>
        <div class="row">
            <div class="col-12">
                <div class="alert alert-info">
                    הדיווחים מתקבלים דרך בוט בטלגרם
                    &bull;
                    <a target="_blank" href="https://telegram.me/opentrain_bot">
                        קישור
                    </a>
                    &bull;
                    לקבלת הדיווחים בזמן אמת ניתן להרשם לערוץ שלנו בטלגרם
                    <a href="https://t.me/opentrain">
                        <span dir="ltr">@opentrain</span>
                    </a>
                </div>
            </div>
        </div>
        <div class="row mb-1" v-if="dataLoaded">
            <div class="col-12">
                <h2 class="d-inline-block">{{ reports.length }} דיווחים
                - {{ uniqueReports.length }} נסיעות
                </h2>
                <div class="btn btn-group float-right">
                    <button class="btn" :class="{'btn-primary disabled': !isGraphMode, 'btn-outline-primary': isGraphMode}" @click="isGraphMode=false">
                        <i class="fal fa-table"></i>
                    </button>
                    <button class="btn" :class="{'btn-primary disabled': isGraphMode, 'btn-outline-primary': !isGraphMode}" @click="isGraphMode=true">
                        <i class="fal fa-chart-bar"></i>
                    </button>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12" v-if="dataLoaded">
                <results-table-view v-show="!isGraphMode" :reports="reports"/>
                <results-graph-view v-show="isGraphMode" :unique-reports="uniqueReports"/>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <div v-if="!dataLoaded && !dataLoadedError" class="text-center">
                    <h4>נתונים נטענים...</h4>
                    <i class="fa fa-spin fa-spinner fa-5x"></i>
                </div>
                <div v-if="!dataLoaded && dataLoadedError" class=" alert-danger alert">
                    שגיאה בקריאת הנתונים. אפשר לנסות שוב עוד מספר דקות. סליחה...
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import ResultsTable from './cr/results-table.vue';
    import ResultsGraph from './cr/results-graph.vue';
    export default {
        data() {
            return {
                reports: [],
                uniqueReports: [],
                dataLoaded: false,
                dataLoadedError: null,
                isGraphMode: false,
            }
        },
        components: {
            resultsTableView: ResultsTable,
            resultsGraphView: ResultsGraph,
        },
        mounted() {
            this.$root.setTitle('דיווחי ביטולים');
            this.getReports();
        },
        methods: {
            getUniqueValidReports() {
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
            async getReports() {
                try {
                    let resp = await this.$axios.get('/api/v1/chatbot/cancel-reports/');
                    this.reports = resp.data;
                    this.uniqueReports = this.getUniqueValidReports();
                    this.dataLoaded = true;
                } catch (err) {
                    console.log(err);
                    this.dataLoadedError = err;
                }
            }
        }
    }
</script>