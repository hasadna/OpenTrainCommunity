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
                <table class="table">
                    <thead>
                    <th>מזהה</th>
                    <th>מקור</th>
                    <th>תאריך דיווח</th>
                    <th>שעת דיווח</th>
                    <th>תחנת מוצא לדיווח</th>
                    <th>תחנת יעד לדיווח</th>
                    <th>תחנת מוצא</th>
                    <th>תחנת יעד</th>
                    <th>מדיה</th>
                    </thead>
                    <tbody>
                    <tr v-for="report in reports">
                        <td>{{ report.id }}</td>
                        <td>
                        <span v-if="report.platform === 'telegram'">
                            <i class="fab fa-telegram-plane"></i>
                        </span>
                            <span v-if="report.platform === 'facebook'">
                            <i class="fab fa-facebook-messenger"></i>
                        </span>
                        </td>
                        <td>{{ report.created_at | to-date }}</td>
                        <td>{{ report.created_at | to-hm }}</td>
                        <td>
                            {{ report.reported_from.name }}
                            {{ report.reported_from.time | hms2hm }}
                        </td>
                        <td>
                            {{ report.reported_to.name }}
                            {{ report.reported_to.time | hms2hm }}
                        </td>
                        <td>
                            {{ report.trip.first_stop.stop_name }}
                            {{ report.trip.first_stop.departure_time | hms2hm }}
                        </td>
                        <td>
                            {{ report.trip.last_stop.stop_name }}
                            {{ report.trip.last_stop.departure_time | hms2hm }}
                        </td>
                        <td>
                            <div v-for="att in report.attachments">
                                <div v-if="att.type === 'image'">
                                    <a target="_blank" :href="att.url">
                                        <img style="max-width: 200px" class="img-fluid"
                                             :src="att.url"></a>
                                </div>
                                <a v-else :href="att.url">
                                    {{ att.type }}
                                </a>
                            </div>
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
            }
        },
        mounted() {
            this.$root.setTitle('דיווחי ביטולים');
            this.getReports();
        },
        methods: {
            async getReports() {
                let resp = await this.$axios.get('/api/v1/chatbot/cancel-reports/');
                this.reports = resp.data;
            }
        }
    }
</script>