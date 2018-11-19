<template>
    <span>{{monthName}} {{year}}</span>
</template>

<script>
    export default {
        props: ['month', 'year'],
        computed: {
            monthName: function() {
                return this.$dtUtils.monthNames[parseInt(this.month)];
            }
        }
    }

</script>
