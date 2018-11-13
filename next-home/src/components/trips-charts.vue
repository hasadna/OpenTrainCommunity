<template lang="html">
    <div class="row">
        <div class="col-sm-6 col-12" :class="{'offset-sm-3': configs.length == 1 }"
             v-for="config in configs">
            <trips-chart :config="config"/>
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
                configs: []
            }
        },
        created() {
            this.buildInitialConfig();
        },
        methods: {
            async buildInitialConfig() {
                let resp = await this.$axios.get("/api/v1/monthly/last-year-month");
                let data = resp.data;
                let [sy, sm] = this.computeStart(data.last_year, data.last_month, 5);
                this.configs.push({
                    endMonth: data.last_month,
                    endYear: data.last_year,
                    startMonth: sm,
                    startYear: sy,
                })
            },
            computeStart(sy, sm, months) {
                let m1 = sy * 12 + sm - 1;
                let m2 = m1 - (months-1);
                let lm = 1 + m2 % 12;
                let ly = (m2 - m2 % 12)/ 12;
                return [ly, lm]
            }
        }
    }
</script>