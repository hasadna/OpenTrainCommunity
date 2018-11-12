<template lang="html">
    <div class="row">
        <div class="col-6" :class="{'offset-3': configs.length == 1 }"
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
                configs: [{
                    startMonth: 1,
                    startYear: 2018,
                    endMonth: 5,
                    endYear: 2018
                }]
            }
        },
    }
</script>