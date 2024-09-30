<template>
  <span>
    <v-btn
      small
      color="error"
      class="ml-5 mr-2"
      @click="isDialogOpen=true"
    ><v-icon small>fa fa-trash-alt</v-icon>
    </v-btn>
    <v-dialog
      v-model="isDialogOpen"
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">Are you sure?</v-card-title>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn
            color="success"
            text
            @click="closeDialog(false)"
          >
            No
          </v-btn>

          <v-btn
            color="error"
            text
            @click="closeDialog(true)"
          >
            Yes
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
    isDialogOpen: false,
    service: Service,
  }),
  methods: {
    async closeDialog(isSave) {
      if (isSave) {
        await this.service.deleteProject(this.project);
        this.$emit('deleted');
      }
      this.projectName = '';
      this.isDialogOpen = false;
    },
  },
};
</script>
