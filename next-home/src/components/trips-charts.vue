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
                <trips-chart :config="config" @remove="remove(config)"/>
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
                globalBegin: null,
                globalEnd: null,
            }
        },
        created() {
            this.buildInitialConfig();
        },
        methods: {
            remove(config) {
                this.configs = this.configs.filter(c=>c!=config);
            },
            async buildInitialConfig() {
                let resp = await this.$axios.get("/api/v1/monthly/year-months/");
                this.globalBegin = resp.data.first;
                this.globalEnd = resp.data.last;
                this.configs.push({
                    end: [...this.globalEnd],
                    months: 5,
                    globalBegin: this.globalBegin,
                    globalEnd: this.globalEnd,
                })
            },
            addNew() {
                this.configs.push({
                    globalBegin: this.globalBegin,
                    globalEnd: this.globalEnd,
                    end: [...this.globalEnd],
                    months: 5,
                })
            }
        }
    }
</script>