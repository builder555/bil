<template>
  <v-row class="text-center">
    <v-col
      cols="12"
      sm="6"
      class="text-left pb-0"
    >
      <span v-if="editingName">
        <v-text-field
          label="Group title"
          v-model="groupName"
          :append-outer-icon="groupName.length > 0 ? 'fa fa-check' : ''"
          @click.stop=""
          @click:append-outer.stop="updateGroupName"
        />
      </span>
      <span v-else @click="toggleEditName">
        {{group.name}}
      </span>
    </v-col>
    <v-col
      cols="4"
      sm="2"
      class="text-right"
      :class="{
        'warning--text': totals.balance > 0,
        'primary--text': totals.balance < 0,
      }"
    >
      {{totals.balance | currency}}
    </v-col>
    <v-col
      cols="4"
      sm="2"
      class="text-right"
      :class="{
        'warning--text': totals.liability > 0,
        'primary--text': totals.liability < 0,
      }"
    >
      {{totals.liability | currency}}
    </v-col>
    <v-col
      cols="4"
      sm="2"
      class="text-right"
      :class="{
        'error--text': totals.asset > 0,
        'success--text': totals.asset < 0,
      }"
    >
      {{totals.asset | currency}}
    </v-col>
    <v-col
      v-if="active"
      cols="12"
      style="cursor:default"
      @click.stop=""
    >
      <v-card rounded="0" elevation="8">
        <v-container class="py-0 mt-0">
          <v-row class="py-0">
            <v-col cols="10" class="py-0">
              <v-text-field
                v-model="paymentSearch"
                label="Search payments"
                clearable
              />
            </v-col>
            <v-col cols="2" class="text-right">
              <v-btn
                icon
                title="Delete group"
                color="error"
                @click="deleteGroup"
              >
                <v-icon> fa fa-trash-alt </v-icon>
              </v-btn>
            </v-col>
          </v-row>
          <v-row class="blue-grey white--text">
            <v-col
              cols="12"
              md="6"
              class="text-left"
            >
              Entry
              <v-btn
                v-if="!payments.find(p => !p.id)"
                small
                color="success"
                class="ml-5 mr-2"
                @click="newPayment"
              >
                <v-icon>fa fa-plus</v-icon>
              </v-btn>
            </v-col>
            <v-col
              cols="4"
              md="2"
              class="text-right"
            >
              Date
            </v-col>
            <v-col
              cols="4"
              md="2"
              class="text-right"
            >
              Owed
              <div>{{totals.liability | currency}}</div>
            </v-col>
            <v-col
              cols="4"
              md="2"
              class="text-right"
            >
              Total
              <div>{{totals.asset | currency}}</div>
            </v-col>
          </v-row>
          <span
            v-for="pay in sortedPayments"
            :key="pay.id"
          >
            <PaymentRow
              :pay="pay"
              @save="savePay"
              @delete="deletePay"
              @setActivePayment="(pay) => activePayment = pay"
            />
        </span>
        </v-container>
      </v-card>
    </v-col>
    <PaymentDetails
      :payment="activePayment"
      @save="savePay"
      @close="activePayment = null"
    />
  </v-row>
</template>

<script>
import { currency } from '@/assets/constants';
import Service from '@/service';
import PaymentDetails from '@/components/PaymentDetails.vue';
import PaymentRow from '@/components/PaymentRow.vue';

export default {
  name: 'PayGroup',
  components: {
    PaymentDetails,
    PaymentRow,
  },
  filters: {
    currency,
  },
  props: {
    active: Boolean,
    group: null,
  },
  data: () => ({
    editingName: false,
    groupName: '',
    paymentSearch: '',
    service: Service,
    activePayment: null,
  }),
  watch: {
    active: {
      immediate: true,
      handler(active) {
        if (!active) return;
        this.groupName = this.group.name;
        this.service.setActiveGroup(this.group.id);
      },
    },
  },
  computed: {
    payments() {
      return this.group.payments;
    },
    filteredPayments() {
      if (this.paymentSearch) {
        const regex = new RegExp(`\\b${this.paymentSearch}`, 'gi');
        return this.payments.filter((pay) => !!pay.name?.match(regex));
      }
      return this.payments;
    },
    sortedPayments() {
      return this.filteredPayments.slice().sort((a, b) => {
        if ((a.date.trim() < b.date.trim()) && a.id) {
          return 1;
        }
        return -1;
      });
    },
    totals() {
      const amounts = {
        liability: 0,
        asset: 0,
        balance: 0,
      };
      let shouldSetBalance = false;
      this.filteredPayments.forEach((payment) => {
        amounts.liability += payment.liability;
        amounts.asset += payment.asset;
        shouldSetBalance ||= payment.liability !== 0;
      });
      amounts.balance = shouldSetBalance ? amounts.liability - amounts.asset : 0;
      return amounts;
    },
  },
  methods: {
    toggleEditName(event) {
      if (this.groupName) {
        event.stopPropagation();
        this.editingName = true;
      }
    },
    paymentUpdated() {
      this.$emit('updated');
    },
    async deleteGroup() {
      const yes = await this.$confirm('Are you sure you sure?', { title: 'Warning' });
      if (yes) {
        await this.service.deleteGroup(this.group.id);
        this.$emit('updated');
      }
    },
    newPayment() {
      const date = [
        new Date().getFullYear(),
        `0${new Date().getMonth() + 1}`.slice(-2),
        `0${new Date().getDate()}`.slice(-2),
      ].join('-');
      const lastPaymentCurrency = this.payments[this.payments.length - 1]?.currency;
      this.activePayment = {
        name: '',
        date,
        asset: 0,
        liability: 0,
        currency: lastPaymentCurrency ?? 'CAD',
      };
    },
    async savePay(payment) {
      if (payment.id) await this.service.updatePayment(payment.id, payment);
      else await this.service.addPayment(payment);
      this.$emit('updated');
    },
    async deletePay(pay) {
      await this.service.deletePay(pay.id);
      this.$emit('updated');
    },
    async updateGroupName() {
      await this.service.updateGroup(this.group.id, { ...this.group, name: this.groupName });
      this.editingName = false;
      this.group.name = this.groupName;
    },
  },
};
</script>
