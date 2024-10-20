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
      scrollable
    >
      <v-card>
        <v-card-title class="headline">
          <v-btn icon @click="isOpen = false">
            <v-icon>fa fa-times</v-icon>
          </v-btn>
          <v-spacer></v-spacer>
          <div>Pick a checkpoint to view</div>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-timeline dense>
            <v-timeline-item
              v-for="h in formattedHistory"
              :key="h.state"
              :class="$route.params.state === h.state ? 'active' : ''"
            >
              <router-link
                :disabled="$route.params.state === h.state"
                :to="{name: 'Home', params: {id: project, state: h.state}}"
              >
                {{h.displayText}}
              </router-link>
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

function formatTimeAgo(datetime) {
  const d = new Date(datetime);
  const now = new Date();
  const diff = now - d;
  const SECOND = 1000;
  const MINUTE = 1000 * 60;
  const HOUR = 1000 * 60 * 60;
  const DAY = 1000 * 60 * 60 * 24;
  if (diff < MINUTE) {
    return `${Math.floor(diff / SECOND)} seconds ago`;
  }
  if (diff < HOUR) {
    return `${Math.floor(diff / MINUTE)} minutes ago`;
  }
  if (diff < DAY) {
    return `${Math.floor(diff / HOUR)} hours ago`;
  }
  if (diff < DAY * 30) {
    return `${Math.floor(diff / DAY)} days ago`;
  }
  return '30+ days ago';
}

export default {
  name: 'TimeMachine',
  props: {
    project: null,
  },
  data: () => ({
    history: [],
    isOpen: false,
  }),
  computed: {
    formattedHistory() {
      const formattedItems = this.history.map((h) => {
        const d = new Date(h.date);
        const date = `${d.getFullYear()}-${`0${d.getMonth() + 1}`.slice(-2)}-${`0${d.getDate()}`.slice(-2)}`;
        const time = `${`0${d.getHours()}`.slice(-2)}:${`0${d.getMinutes()}`.slice(-2)}`;
        const ago = formatTimeAgo(h.date);
        return {
          displayText: `${date}@${time} (${ago})`,
          state: h.id,
        };
      });
      return [{ state: null, displayText: 'Current' }, ...formattedItems];
    },
  },
  methods: {
    async viewHistory() {
      this.isOpen = true;
      this.history = await Service.getProjectHistory(this.project);
    },
  },
};
</script>
