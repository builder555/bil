<template>
  <span>
    <v-icon v-if="project" @click="viewHistory">fa fa-clock-rotate-left</v-icon>
  </span>
</template>
<script>
import Service from '@/service';

export default {
  name: 'TimeMachine',
  props: {
    project: null,
  },
  methods: {
    async viewHistory() {
      const hist = await Service.getProjectHistory(this.project);
      console.log(hist);
    },
  },
};
</script>
