<template>
  <span>
    <v-btn
      small
      color="success"
      class="ml-5 mr-2"
      @click="isNewProject=true"
    >
      Add Project <v-icon small right>fa fa-plus</v-icon>
    </v-btn>
    <v-dialog
      v-model="isNewProject"
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">Create new project</v-card-title>

        <v-card-text>
          <v-text-field v-model="projectName" label="Project Name"/>
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
            :disabled="!projectName.trim()"
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
  data: () => ({
    isNewProject: false,
    projectName: '',
    service: Service,
  }),
  methods: {
    async closeDialog(isSave) {
      if (isSave) {
        await this.service.addProject(this.projectName);
        this.$emit('created');
      }
      this.projectName = '';
      this.isNewProject = false;
    },
  },
};
</script>
