<template>
    <span>{{monthName}} {{year}}</span>
</template>

<script>
    const months = [
        '',
        'ינואר',
        'פברואר',
        'מרץ',
        'אפריל',
        'מאי',
        'יוני',
        'יולי',
        'אוגוסט',
        'ספטמבר',
        'אוקטובר',
        'נובמבר',
        'דצמבר',
    ];


    export default {
        props: ['month', 'year'],
        computed: {
            monthName: function() {
                return months[parseInt(this.month)];
            }
        }
    }

</script>
