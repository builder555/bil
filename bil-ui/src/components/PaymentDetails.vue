<template>
  <v-dialog
    v-model="isDialogOpen"
    max-width="290"
  >
    <v-card v-if="localPay">
      <v-form @submit.prevent="closeDialog(true)">
        <v-card-text class="pb-0">
          <v-container class="pa-0">
            <v-row dense>
              <v-text-field v-model="localPay.name" label="Name" autofocus/>
            </v-row>
            <v-row dense>
              <v-col>
                <v-select
                  v-model="localPay.currency"
                  :items="currencies"
                  label="Currency"
                  :return-object="false"
                  auto-select-first
                />
              </v-col>
              <v-col>
                <v-text-field
                  type="number"
                  v-model="localPay.liability"
                  label="Owed"
                  inputmode="decimal"
                >
                  <template v-slot:prepend-inner>
                    <v-icon
                      x-small
                      :class="['fa', localPay.liability < 0 ? 'fa-plus-circle' : 'fa-minus-circle']"
                      @click="localPay.liability = -localPay.liability"
                    />
                  </template>
                </v-text-field>
              </v-col>
              <v-col>
                <v-text-field
                  type="number"
                  v-model="localPay.asset"
                  label="Paid"
                  inputmode="decimal"
                >
                  <template v-slot:prepend-inner>
                    <v-icon
                      x-small
                      :class="['fa', localPay.asset < 0 ? 'fa-plus-circle' : 'fa-minus-circle']"
                      @click="localPay.asset = -localPay.asset"
                    />
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
            <v-text-field
              v-model="localPay.date"
              label="Date"
              v-mask="'####-##-##'"
              inputmode="numeric"
            />
          </v-container>
        </v-card-text>
        <v-card-actions class="pt-0">
          <v-spacer></v-spacer>
          <v-btn
            color="warning"
            text
            @click="closeDialog(false)"
          >
            Cancel
          </v-btn>
          <v-btn
            color="success"
            text
            :disabled="!isPayValid"
            type="submit"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>
<script>
import { mask } from 'vue-the-mask';

export default {
  name: 'Payment',
  directives: { mask },
  props: {
    payment: null,
  },
  data: () => ({
    isDialogOpen: false,
    localPay: null,
    currencies: ['CAD', 'USD', 'GBP', 'EUR'],
  }),
  computed: {
    isPayValid() {
      const isDateValid = (new Date(this.localPay?.date)).toString().toLowerCase() !== 'invalid date';
      return this.localPay?.name.length > 0
          && isDateValid
          && !Number.isNaN(parseFloat(this.localPay?.asset))
          && !Number.isNaN(parseFloat(this.localPay?.liability))
          && (
            this.localPay.asset !== 0 || this.localPay.liability !== 0
          );
    },
  },
  watch: {
    payment() {
      if (!this.payment) return;
      this.isDialogOpen = true;
      this.localPay = JSON.parse(JSON.stringify(this.payment));
    },
    isDialogOpen() {
      if (this.isDialogOpen) return;
      this.$emit('close');
    },
  },
  methods: {
    closeDialog(emitSave) {
      this.isDialogOpen = false;
      if (emitSave) {
        this.$emit('save', this.localPay);
      }
    },
  },
};
</script>
