<template>
  <v-btn
    icon
    title="Dark mode"
    :color="$vuetify.theme.dark ? 'orange' : ''"
    @click.native="toggleDarkMode"
  >
    <v-icon>fa fa-moon</v-icon>
  </v-btn>
</template>
<script>
export default {
  methods: {
    toggleDarkMode() {
      this.$vuetify.theme.dark = !this.$vuetify.theme.dark;
      localStorage.setItem('darkMode', JSON.stringify(this.$vuetify.theme.dark));
    },
  },
  mounted() {
    this.$vuetify.theme.dark = JSON.parse(localStorage.getItem('darkMode') || 'false');
  },
};
</script>
