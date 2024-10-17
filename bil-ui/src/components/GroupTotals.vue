<template>
  <v-card class="px-2">
    <v-row class="pa-0">
      <v-col cols="12" class="pb-1 text-center">Group Totals</v-col>
      <v-col cols="12" class="pt-0"><hr></v-col>
      <v-col cols="6" class="py-0">Balance: </v-col>
      <v-col cols="6"
        class="text-right py-0"
        :class="{
          'warning--text': totals.balance > 0,
          'primary--text': totals.balance < 0,
        }"
      >{{totals.balance | currency}}</v-col>
      <v-col cols="6" class="py-0">Owed:</v-col>
      <v-col cols="6"
        class="text-right py-0"
        :class="{
          'warning--text': totals.owed > 0,
          'primary--text': totals.owed < 0,
        }"
      >{{totals.owed | currency}}</v-col>
      <v-col cols="6" class="py-0">Paid:</v-col>
      <v-col cols="6"
        class="text-right py-0"
        :class="{
          'error--text': totals.paid > 0,
          'success--text': totals.paid < 0,
        }"
      >{{totals.paid | currency}}</v-col>
    </v-row>
  </v-card>
</template>

<script>
import { currency } from '../assets/constants';

export default {
  name: 'GroupTotals',
  props: {
    totals: Object,
  },
  filters: {
    currency,
  },
};
</script>
