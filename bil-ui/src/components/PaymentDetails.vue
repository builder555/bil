<template>
  <v-dialog
    v-model="isDialogOpen"
    max-width="350"
    >
    <v-card
      v-if="localPayment"
      @dragover.stop.prevent="onDragOver"
      @dragleave.stop.prevent="onDragLeave"
      @drop.stop.prevent="onDrop"
    >
      <v-form
        ref="dialog"
        @submit.prevent="closeDialog(true)"
      >
        <v-card-text class="pb-0">
          <v-container class="pa-0">
            <v-row dense>
              <v-text-field v-model="localPayment.name" label="Name" autofocus />
            </v-row>
            <v-row dense>
              <v-col>
                <v-select v-model="localPayment.currency" :items="currencies" label="Currency" :return-object="false"
                  auto-select-first />
              </v-col>
              <v-col>
                <v-text-field type="number" v-model="localPayment.owed" label="Owed" inputmode="decimal">
                  <template
                    v-if="isTouchDevice"
                    v-slot:prepend-inner
                  >
                    <v-icon
                      x-small
                      tabindex="-1"
                      :class="['fa', localPayment.owed < 0 ? 'fa-plus-circle' : 'fa-minus-circle']"
                      @click="localPayment.owed = -localPayment.owed"
                    />
                  </template>
                </v-text-field>
              </v-col>
              <v-col>
                <v-text-field type="number" v-model="localPayment.paid" label="Paid" inputmode="decimal">
                  <template
                    v-if="isTouchDevice"
                    v-slot:prepend-inner
                  >
                    <v-icon
                      x-small
                      tabindex="-1"
                      :class="['fa', localPayment.paid < 0 ? 'fa-plus-circle' : 'fa-minus-circle']"
                      @click="localPayment.paid = -localPayment.paid"
                      />
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
            <v-text-field v-model="localPayment.date" label="Date" v-mask="'####-##-##'" inputmode="numeric" />
          </v-container>
        </v-card-text>
        <v-card-actions class="pt-0">
          <v-spacer
            v-if="localPayment.attachment"
            class="pa-0 text-center"
          >
            <a :href="url" target="_blank">{{localPayment.attachment}}</a>
          </v-spacer>
          <v-spacer
            v-else
            class="pa-0 text-center"
          >
            {{attachment}}
          </v-spacer>
          <v-btn
            color="warning"
            text
            @click="closeDialog(false)"
          >Cancel</v-btn>
          <v-btn
            color="success"
            text
            :disabled="!isPayValid"
            type="submit"
          >Save</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>
<script>
import { mask } from 'vue-the-mask';
import Service from '@/service';

export default {
  name: 'Payment',
  directives: { mask },
  props: {
    payment: null,
  },
  data: () => ({
    isDialogOpen: false,
    localPayment: null,
    currencies: ['CAD', 'USD', 'GBP', 'EUR'],
    file: null,
    hovered: false,
    service: Service,
  }),
  computed: {
    isTouchDevice() {
      return (('ontouchstart' in window)
        || (navigator.maxTouchPoints > 0)
        || (navigator.msMaxTouchPoints > 0));
    },
    isPayValid() {
      const isDateValid = (new Date(this.localPayment?.date)).toString().toLowerCase() !== 'invalid date';
      return this.localPayment?.name.length > 0
        && isDateValid
        && !Number.isNaN(parseFloat(this.localPayment?.paid))
        && !Number.isNaN(parseFloat(this.localPayment?.owed));
    },
    url() {
      const { baseUrl, projectId, payGroupId } = this.service;
      const { id } = this.localPayment;
      return `${baseUrl}/projects/${projectId}/paygroups/${payGroupId}/payments/${id}/files`;
    },
    attachment() {
      if (this.file) return 'Attached file';
      if (this.localPayment?.attachment) return this.url;
      return 'Drop file';
    },
  },
  watch: {
    payment() {
      if (!this.payment) return;
      this.isDialogOpen = true;
      this.localPayment = JSON.parse(JSON.stringify(this.payment));
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
        this.$emit('save', this.localPayment, this.file);
      }
    },
    onDragOver() {
      if (this.hovered) return;
      this.hovered = true;
      this.$refs.dialog.$el.classList.add('drag-over');
    },
    onDrop(e) {
      [this.file] = e.dataTransfer.files;
      this.onDragLeave();
    },
    onDragLeave() {
      if (!this.hovered) return;
      this.hovered = false;
      this.$refs.dialog.$el.classList.remove('drag-over');
    },
  },
};
</script>
<style scoped>
#drop-zone {
  height: 30px;
}

.drag-over {
  background: #ffffff00;
  background-image: radial-gradient(#777 1px, transparent 0);
  background-size: 30px 30px;
  background-position: 10px 10px;
}
</style>
