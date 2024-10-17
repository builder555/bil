<template>
  <span>
    <v-icon v-if="project" @click="viewHistory">fa fa-clock-rotate-left</v-icon>
    <!-- display datetimes for previous states -->
     <div>
       <ul>
        <li v-for="h in history" :key="h.id"> {{ h.date }}</li>
       </ul>
     </div>
  </span>
</template>
<script>
import Service from '@/service';

export default {
  name: 'TimeMachine',
  props: {
    project: null,
  },
  data: () => ({
    history: [],
  }),
  methods: {
    async viewHistory() {
      this.history = await Service.getProjectHistory(this.project);
      console.log(this.history);
    },
  },
};
</script>
