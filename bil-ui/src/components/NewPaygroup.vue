<template>
  <span>
    <v-btn
      small
      color="success"
      class="ml-5 mr-2"
      @click="isOpen=true"
    >
      <v-icon>fa fa-plus</v-icon>
    </v-btn>
    <v-dialog
      v-model="isOpen"
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">Add new paygroup</v-card-title>

        <v-card-text>
          <v-text-field v-model="name" label="Group Name"/>
        </v-card-text>

        <v-card-actions>
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
            :disabled="!name.trim()"
            @click="closeDialog(true)"
          >
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </span>
</template>
<script>
import Service from '@/service';

export default {
  props: {
    project: null,
  },
  data: () => ({
    isOpen: false,
    name: '',
    service: Service,
  }),
  methods: {
    async closeDialog(isSave) {
      if (isSave && this.project) {
        await this.service.addGroup(this.project, this.name);
        this.$emit('created');
      }
      this.name = '';
      this.isOpen = false;
    },
  },
};
</script>
