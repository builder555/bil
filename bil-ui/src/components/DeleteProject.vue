<template>
  <span>
    <v-btn
      small
      color="error"
      class="ml-5 mr-2"
      @click="confirmDelete"
    ><v-icon small>fa fa-trash-alt</v-icon>
    </v-btn>
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
    async confirmDelete() {
      const yes = await this.$confirm('Delete this project?', { title: 'Warning' });
      if (yes) {
        await this.service.deleteProject(this.project);
        this.$emit('deleted');
      }
    },
  },
};
</script>
