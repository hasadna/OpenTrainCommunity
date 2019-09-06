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
                <div class="btn btn-group">
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
            <div class="col-12" v-if="this.dataLoaded">
                <results-table-view v-if="!isGraphMode" :reports="reports"/>
                <results-graph-view v-if="isGraphMode" :reports="reports"/>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <div v-if="!dataLoaded" class="text-center">
                    <h4>נתונים נטענים...</h4>
                    <i class="fa fa-spin fa-spinner fa-5x"></i>
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
                dataLoaded: false,
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
            async getReports() {
                let resp = await this.$axios.get('/api/v1/chatbot/cancel-reports/');
                this.reports = resp.data;
                this.dataLoaded = true;
            }
        }
    }
</script>