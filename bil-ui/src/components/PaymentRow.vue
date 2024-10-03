<template>
  <v-row
    v-if="localPay"
    class="row-pay secondary"
    v-touch="{
      left: () => toggleDelete(localPay, true),
      right: () => toggleDelete(localPay, false),
    }"
    @click="toggleEdit(localPay)"
  >
    <v-col cols="12" md="6" class="text-left py-2">
      <v-chip x-small class="px-1">{{localPay.currency}}</v-chip>
      {{localPay.name}}
      <v-icon v-if="localPay.attachment" x-small class="text-right">fa fa-paperclip</v-icon>
    </v-col>
    <v-col cols="4" md="2" class="text-right py-0 py-md-2">{{localPay.date}}</v-col>
    <v-col cols="4" md="2" class="text-right py-0 py-md-2">{{localPay.liability | currency}}</v-col>
    <v-col cols="4" md="2" class="text-right py-0 py-md-2">{{localPay.asset | currency}}</v-col>
    <div
      class="payrow-hover-buttons"
      :class="{
        'd-block': localPay.isTrashVisible
      }"
    >
      <v-btn
        v-show="localPay.liability !== localPay.asset || localPay.changed"
        small
        :color="localPay.changed ? 'warning' : 'info'"
        class="mt-1"
        @click.stop="localPay.changed ? undoCopy(localPay) : copyPaidToOwed(localPay)"
      >
        <v-icon v-if="!localPay.changed">far fa-arrow-alt-circle-left</v-icon>
        <v-icon v-else>fas fa-times</v-icon>
      </v-btn>
      <v-btn
        v-show="localPay.liability !== localPay.asset || localPay.changed"
        small
        color="info"
        class="mt-1"
        @click.stop="localPay.changed ? savePay(localPay) :copyOwedToPaid(localPay)"
      >
        <v-icon v-if="!localPay.changed">far fa-arrow-alt-circle-right</v-icon>
        <v-icon v-else>fas fa-check</v-icon>
      </v-btn>
      <v-btn
        small
        color="error"
        class="mt-1"
        @click.stop="deletePayment(localPay.id)"
      >
        <v-icon>fa fa-trash-alt</v-icon>
      </v-btn>
    </div>
  </v-row>
</template>

<script>
import { currency } from '@/assets/constants';

export default {
  props: ['pay'],
  filters: {
    currency,
  },
  data: () => ({
    localPay: null,
  }),
  watch: {
    pay: {
      immediate: true,
      handler() {
        this.localPay = JSON.parse(JSON.stringify(this.pay));
      },
    },
  },
  methods: {
    copyPaidToOwed(pay) {
      pay.originalOwed = pay.liability;
      pay.liability = pay.asset;
      this.$set(pay, 'changed', true);
    },
    copyOwedToPaid(pay) {
      pay.originalAmount = pay.asset;
      pay.asset = pay.liability;
      this.$set(pay, 'changed', true);
    },
    undoCopy(pay) {
      if (pay.originalOwed !== undefined) pay.liability = pay.originalOwed;
      if (pay.originalAmount !== undefined) pay.asset = pay.originalAmount;
      this.$set(pay, 'changed', false);
    },
    async deletePayment(id) {
      const yes = await this.$confirm('Are you sure you sure?', { title: 'Warning' });
      if (yes) {
        this.$emit('delete', id);
      }
    },
    async savePay(payment) {
      this.$emit('save', payment);
    },
    toggleEdit(pay) {
      this.$emit('setActivePayment', JSON.parse(JSON.stringify(pay)));
    },
    toggleDelete(pay, isVisible) {
      this.$set(pay, 'isTrashVisible', isVisible);
    },
  },
};
</script>
<style scoped>
.payrow-hover-buttons {
  display:none;
  position:absolute;
  right:0;
}
.payrow-hover-buttons * {
  margin-left:5px;
}
@media (pointer:fine) {
  .row-pay:hover .payrow-hover-buttons {
    display:block;
  }
}
</style>
