<template>
  <v-row
    v-if="pay"
    class="row-pay secondary"
    v-touch="{
      left: () => toggleDelete(pay, true),
      right: () => toggleDelete(pay, false),
    }"
    @click="toggleEdit(pay)"
  >
    <v-col cols="12" md="6" class="text-left py-2">
      <v-chip x-small class="px-1">{{pay.currency}}</v-chip>
      {{pay.name}}
      <v-icon v-if="pay.attachment" x-small class="text-right">fa fa-paperclip</v-icon>
    </v-col>
    <v-col cols="4" md="2" class="text-right py-0 py-md-2">{{pay.date}}</v-col>
    <v-col cols="4" md="2" class="text-right py-0 py-md-2">{{pay.liability | currency}}</v-col>
    <v-col cols="4" md="2" class="text-right py-0 py-md-2">{{pay.asset | currency}}</v-col>
    <div
      class="payrow-hover-buttons"
      :class="{
        'd-block': pay.isTrashVisible
      }"
    >
      <v-btn
        v-show="pay.liability !== pay.asset || pay.changed"
        small
        :color="pay.changed ? 'warning' : 'info'"
        class="mt-1"
        @click.stop="pay.changed ? undoCopy(pay) : copyPaidToOwed(pay)"
      >
        <v-icon v-if="!pay.changed">far fa-arrow-alt-circle-left</v-icon>
        <v-icon v-else>fas fa-times</v-icon>
      </v-btn>
      <v-btn
        v-show="pay.liability !== pay.asset || pay.changed"
        small
        color="info"
        class="mt-1"
        @click.stop="pay.changed ? savePay(pay) :copyOwedToPaid(pay)"
      >
        <v-icon v-if="!pay.changed">far fa-arrow-alt-circle-right</v-icon>
        <v-icon v-else>fas fa-check</v-icon>
      </v-btn>
      <v-btn
        small
        color="error"
        class="mt-1"
        @click.stop="deletePayment(pay.id)"
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
  methods: {
    copyPaidToOwed(pay) {
      // eslint-disable-next-line
      pay.originalOwed = pay.liability;
      // eslint-disable-next-line
      pay.liability = pay.asset;
      this.$set(pay, 'changed', true);
    },
    copyOwedToPaid(pay) {
      // eslint-disable-next-line
      pay.originalAmount = pay.asset;
      // eslint-disable-next-line
      pay.asset = pay.liability;
      this.$set(pay, 'changed', true);
    },
    undoCopy(pay) {
      // eslint-disable-next-line
      if (pay.originalOwed !== undefined) pay.liability = pay.originalOwed;
      // eslint-disable-next-line
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
