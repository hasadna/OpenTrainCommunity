<template lang="html">
    <div>
        <div class="row">
            <div class="col-12 col-sm-6">
                <table class="table">
                    <thead>
                    <tr>
                        <th>שעה</th>
                        <th>תחנה</th>
                        <th>דיווחים</th>
                    </tr>
                    </thead>
                    <tbody>
                        <tr v-for="stop in stops">
                            <td>
                                {{ stop.departure_time | hms2hm }}
                            </td>
                            <td>
                                {{ stop.stop_name }}
                            </td>
                            <td>
                                <span v-if="stop.reports.length >= 1">
                                <span class="badge badge-pill badge-primary">
                                    {{ stop.reports.length }}
                                </span>
                            </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                reports: [],
                id: null,
                trip: null,
                stops: null
            }
        },
        mounted() {
            this.id = this.$route.params.id;
            this.$root.setTitle('פרטי דיווח');
            this.getTripDetails();
        },
        methods: {
            async getTripDetails() {
                let resp = await this.$axios.get(`/api/v1/chatbot/trips/${this.id}/`);
                this.trip = resp.data;
                this.stops = this.trip.reports[0].stops;
                let stopsByCode = {};
                for (let stop of this.stops) {
                    stopsByCode[stop.stop_code] = stop;
                    stop.reports = [];
                }

                for (let report of this.trip.reports) {
                    stopsByCode[report.reported_from.code].reports.push(report);
                }
            }
        }
    }
</script>