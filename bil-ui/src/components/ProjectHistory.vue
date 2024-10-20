<template>
  <span>
    <v-icon
      v-if="project"
      @click="viewHistory"
    >fa fa-clock-rotate-left</v-icon>
    <v-dialog
      v-if="history.length"
      max-width="400"
      v-model="isOpen"
    >
      <v-card>
        <v-card-title class="headline">Pick a checkpoint to view</v-card-title>
        <v-card-text>
          <v-timeline dense>
            <v-timeline-item v-for="h in history" :key="h.id">
              {{ h.date }}
            </v-timeline-item>
          </v-timeline>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
    isOpen: false,
  }),
  methods: {
    async viewHistory() {
      this.isOpen = true;
      this.history = await Service.getProjectHistory(this.project);
    },
  },
};
</script>
