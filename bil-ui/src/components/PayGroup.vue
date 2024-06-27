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
          append-outer-icon="fa-check"
          @click.stop=""
          @click:append-outer.stop="updateGroupName"
        />
      </span>
      <span v-else @click.stop="editingName=true">
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
        'warning--text': group.owed > 0,
        'primary--text': group.owed < 0,
      }"
    >
      {{group.owed | currency}}
    </v-col>
    <v-col
      cols="4"
      sm="2"
      class="text-right"
      :class="{
        'error--text': group.total > 0,
        'success--text': group.total < 0,
      }"
    >
      {{group.total | currency}}
    </v-col>
    <v-col
      cols="12"
      v-if="active"
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
              <div>{{totals.owed | currency}}</div>
            </v-col>
            <v-col
              cols="4"
              md="2"
              class="text-right"
            >
              Total
              <div>{{totals.paid | currency}}</div>
            </v-col>
          </v-row>
          <v-row
            v-for="pay in sortedPayments"
            :key="pay.id"
            class="row-pay secondary"
            v-touch="{
              left: () => toggleDelete(pay, true),
              right: () => toggleDelete(pay, false),
            }"
            @click="toggleEdit(pay, true)"
          >
            <v-col
              cols="12"
              md="6"
              class="text-left pb-0 pt-2"
            >
              <div v-if="!!pay.editing">
                <v-row class="my-0 py-0">
                  <v-col cols="2" class="my-0 py-0">
                    <v-autocomplete
                      :items="currencies"
                      item-text="name"
                      item-value="id"
                      label="Currency"
                      :return-object="false"
                      auto-select-first
                    />
                  </v-col>
                  <v-col cols="10" class="my-0 py-0">
                    <v-text-field
                      v-model="pay.editing.name"
                      label="Name"
                    />
                  </v-col>
                </v-row>
              </div>
              <div v-else>
                {{pay.name}}
              </div>
            </v-col>
            <v-col
              cols="4"
              md="2"
              class="text-right py-0 py-md-2"
            >
              <div v-if="!!pay.editing">
                <v-text-field
                  v-model="pay.editing.when"
                  label="Date"
                />
              </div>
              <div v-else>{{pay.when}}</div>
            </v-col>
            <v-col
              cols="4"
              md="2"
              class="text-right py-0 py-md-2"
            >
              <div v-if="!!pay.editing">
                <v-text-field
                  v-model="pay.editing.owed"
                  label="Owed"
                  type="number"
                />
              </div>
              <div v-else>{{pay.owed | currency}}</div>
            </v-col>
            <v-col
              cols="4"
              md="2"
              class="text-right py-0 py-md-2"
            >
              <div v-if="!!pay.editing">
                <v-text-field
                  v-model="pay.editing.amount"
                  label="Paid"
                  type="number"
                  append-outer-icon="fa-times"
                  :append-icon="isPayValid(pay.editing) ? 'fa-check' : ''"
                  @click:append="savePay(pay.editing)"
                  @click:append-outer="toggleEdit(pay, false)"
                />
              </div>
              <div v-else>{{pay.amount | currency}}</div>
            </v-col>
            <div
              class="payrow-hover-buttons"
              :class="{
                'd-block': pay.isTrashVisible
              }"
            >
              <v-btn
                v-show="!pay.editing && (pay.owed !== pay.amount || pay.changed)"
                small
                :color="pay.changed ? 'warning' : 'info'"
                class="mt-1"
                @click.stop="pay.changed ? undoCopy(pay) : copyPaidToOwed(pay)"
              >
                <v-icon v-if="!pay.changed">far fa-arrow-alt-circle-left</v-icon>
                <v-icon v-else>fas fa-times</v-icon>
              </v-btn>
              <v-btn
                v-show="!pay.editing && (pay.owed !== pay.amount || pay.changed)"
                small
                color="info"
                class="mt-1"
                @click.stop="pay.changed ? savePay(pay) :copyOwedToPaid(pay)"
              >
                <v-icon v-if="!pay.changed">far fa-arrow-alt-circle-right</v-icon>
                <v-icon v-else>fas fa-check</v-icon>
              </v-btn>
              <v-btn
                v-show="!pay.editing"
                small
                color="error"
                class="mt-1"
                @click.stop="deletePayment(pay)"
              >
                <v-icon>fa fa-trash-alt</v-icon>
              </v-btn>
            </div>
          </v-row>
        </v-container>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import { currency } from '@/assets/constants';
import Service from '@/service';

export default {
  name: 'PayGroup',
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
    payments: [],
    paymentSearch: '',
    service: Service,
    currencies: [
      { symbol: '$', name: 'CAD', id: 0 },
      { symbol: '$', name: 'USD', id: 1 },
      { symbol: '£', name: 'GBP', id: 2 },
      { symbol: '€', name: 'EUR', id: 3 },
    ],
  }),
  watch: {
    active: {
      immediate: true,
      handler() {
        this.getPayments();
        this.groupName = this.group.name;
      },
    },
  },
  computed: {
    filteredPayments() {
      if (this.paymentSearch) {
        const lowerPaySearch = this.paymentSearch.toLowerCase();
        return this.payments.filter((pay) => !!pay.editing
                                          || pay.name.toLowerCase().indexOf(lowerPaySearch) === 0
                                          || pay.name.toLowerCase().indexOf(` ${lowerPaySearch}`) >= 0);
      }
      return this.payments;
    },
    sortedPayments() {
      return this.filteredPayments.slice().sort((a, b) => {
        if ((a.when.trim() < b.when.trim()) && a.id) {
          return 1;
        }
        return -1;
      });
    },
    totals() {
      const amounts = {
        owed: 0,
        paid: 0,
        balance: 0,
      };
      this.filteredPayments.forEach((payment) => {
        amounts.owed += Number.isNaN(+payment.owed) ? 0 : +payment.owed;
        amounts.paid += Number.isNaN(+payment.amount) ? 0 : +payment.amount;
      });
      if (+this.group.owed !== 0) {
        amounts.balance = +this.group.owed - +this.group.total;
      }
      return amounts;
    },
  },
  methods: {
    undoCopy(pay) {
      // eslint-disable-next-line
      if (pay.originalOwed !== undefined) pay.owed = pay.originalOwed;
      // eslint-disable-next-line
      if (pay.originalAmount !== undefined) pay.amount = pay.originalAmount;
      this.$set(pay, 'changed', false);
    },
    copyPaidToOwed(pay) {
      // eslint-disable-next-line
      pay.originalOwed = pay.owed;
      // eslint-disable-next-line
      pay.owed = pay.amount;
      this.$set(pay, 'changed', true);
    },
    copyOwedToPaid(pay) {
      // eslint-disable-next-line
      pay.originalAmount = pay.amount;
      // eslint-disable-next-line
      pay.amount = pay.owed;
      this.$set(pay, 'changed', true);
    },
    async deletePayment(pay) {
      const yes = await this.$confirm('Are you sure you want to delete this payment?', {
        title: 'Warning',
      });
      if (yes) {
        if (pay.id) {
          await this.service.deletePay(pay.id);
        }
        this.payments.splice(this.payments.findIndex((item) => item === pay), 1);
        this.$emit('updated');
      }
    },
    async deleteGroup() {
      const yes = await this.$confirm('Are you sure you want to delete this group and all its entries?', {
        title: 'Warning',
      });
      if (yes && this.group.id) {
        await this.service.deleteGroup(this.group.id);
        this.$emit('updated');
      }
    },
    async getPayments() {
      if (this.active) {
        this.payments = await this.service.getPayments(this.group.id);
      }
    },
    isPayValid(pay) {
      return pay.name.length > 0
          && pay.when.length > 0
          && !Number.isNaN(parseFloat(pay.amount))
          && !Number.isNaN(parseFloat(pay.owed));
    },
    newPayment() {
      const d = new Date();
      const when = [
        d.getFullYear(),
        `0${d.getMonth() + 1}`.slice(-2),
        `0${d.getDate()}`.slice(-2),
      ].join('-');
      this.payments.push({
        editing: {
          name: '',
          when,
          paygroup: this.group.id,
          amount: 0,
          owed: 0,
        },
        when: '',
      });
    },
    async savePay(payment) {
      if (!this.isPayValid(payment)) return;
      if (payment.id) {
        await this.service.updatePayment(payment.id, payment);
      } else {
        await this.service.addPayment(payment);
      }
      await this.getPayments();
      this.$emit('updated');
    },
    toggleEdit(pay, isEditing) {
      if (!!pay.editing === !!isEditing) return;
      if (isEditing) {
        this.payments.forEach((p) => {
          if (p === pay) this.$set(pay, 'editing', JSON.parse(JSON.stringify(pay)));
          else if (p.editing) this.$set(p, 'editing', null);
        });
      } else if (pay.id) this.$set(pay, 'editing', null);
      else this.deletePayment(pay);
    },
    toggleDelete(pay, isVisible) {
      this.$set(pay, 'isTrashVisible', isVisible);
    },
    async updateGroupName() {
      await this.service.updateGroup(this.group.id, { ...this.group, name: this.groupName });
      this.editingName = false;
      this.group.name = this.groupName;
    },
  },
};
</script>
<style>
.row-pay:nth-child(odd) {
  background: initial !important;
}
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
input[type="number"] {
  appearance: textfield;
  -moz-appearance: textfield;
}
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
