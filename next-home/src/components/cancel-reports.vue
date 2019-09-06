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
        <div class="row">
            <div class="col-12">
                <results-table-view :reports="reports"/>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <p v-if="!dataLoaded" class="text-center">
                    <i class="fa fa-spin fa-spinner fa-5x"></i>
                </p>

            </div>
        </div>
    </div>
</template>

<script>
    import ResultsTable from './results-table.vue';

    export default {
        data() {
            return {
                reports: [],
                dataLoaded: false,
            }
        },
        components: {
            resultsTableView: ResultsTable
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