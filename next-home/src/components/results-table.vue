<template>
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
        <th>מזהה נסיעה</th>
        <th>מדיה</th>
        </thead>
        <tbody>
        <tr v-for="report in reports" :class="{'wrong-report': report.wrong_report}">
            <td>
                        <span v-if="report.wrong_report" title="הדיווח ככל הנראה שגוי" class="text-danger">
                            <i class="far fa-exclamation-square"></i>
                        </span>
                {{ report.id }}
            </td>
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
                {{ report.first_stop.stop_name }}
                {{ report.first_stop.departure_time | hms2hm }}
            </td>
            <td>
                {{ report.last_stop.stop_name }}
                {{ report.last_stop.departure_time | hms2hm }}
            </td>
            <td>
                <code dir="ltr">
                    <router-link :to="{ name: 'trip-details', params: { id: report.trip }}">
                        {{ report.gtfs_trip_id }}
                    </router-link>
                </code>
                &nbsp;
                <span v-if="report.gtfs_trip_id_reports >= 2">
                                <span class="badge badge-pill badge-primary">
                                    {{report.gtfs_trip_id_reports}}
                                </span>
                            </span>
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
</template>

<script>
    export default {
        props: ['reports'],
    }
</script>
