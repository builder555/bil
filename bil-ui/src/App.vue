<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
    >
      <v-autocomplete
        v-model="project"
        :items="projects"
        item-text="name"
        item-value="id"
        label="Projects"
        class="mt-5"
        clearable
        no-data-text="No projects found"
        :return-object="false"
        auto-select-first
      />
      <delete-project v-if="project" :project="project" @deleted="getProjects()" />
      <new-project @created="getProjects()"/>
      <dark-toggle/>
    </v-app-bar>
    <v-main v-if="project">
      <v-container>
        <v-row>
          <v-col cols="12" offset-sm="6" sm="6" offset-md="8" md="4">
            <v-card class="px-2">
              <v-row>
                <v-col cols="6">Balance: </v-col>
                <v-col cols="6"
                  class="text-right"
                  :class="{
                    'warning--text': totals.balance > 0,
                    'primary--text': totals.balance < 0,
                  }"
                >{{totals.balance | currency}}</v-col>
              </v-row>
              <v-row>
                <v-col cols="6">Owed:</v-col>
                <v-col cols="6"
                  class="text-right"
                  :class="{
                    'warning--text': totals.liability > 0,
                    'primary--text': totals.liability < 0,
                  }"
                >{{totals.liability | currency}}</v-col>
              </v-row>
              <v-row>
                <v-col cols="6">Paid:</v-col>
                <v-col cols="6"
                  class="text-right"
                  :class="{
                    'error--text': totals.asset > 0,
                    'success--text': totals.asset < 0,
                  }"
                >{{totals.asset | currency}}</v-col>
              </v-row>
            </v-card>
          </v-col>
        </v-row>
        <v-text-field
          v-model="groupSearch"
          label="Search groups"
          clearable
        />
        <v-row class="indigo darken-1 white--text">
          <v-col
            cols="12"
            sm="6"
            class="text-left"
          >
            Payment Group
            <new-paygroup
              :project="project"
              @created="getGroups"
            />
          </v-col>
          <v-col cols="4" sm="2" class="text-right">Balance</v-col>
          <v-col cols="4" sm="2" class="text-right">Owed</v-col>
          <v-col cols="4" sm="2" class="text-right">Paid</v-col>
        </v-row>
        <pay-group
          v-for="group in sortedGroups"
          :key="`pay-group-${group.id}`"
          :group="group"
          class="pay-group accent"
          :class="[{'is-active': group.id === activeGroup}]"
          :active="group.id === activeGroup"
          style="cursor:pointer"
          @click.native="setActiveGroup(group.id)"
          @updated="getGroups"
        />
      </v-container>
    </v-main>
    <v-main v-else>
      <v-container>
        <v-row>
          <v-col>
            <v-alert class="primary" dark>Select a project</v-alert>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
    <v-spacer></v-spacer>
  </v-app>
</template>

<script>
import PayGroup from '@/components/PayGroup.vue';
import DarkToggle from '@/components/DarkToggle.vue';
import NewProject from '@/components/NewProject.vue';
import DeleteProject from '@/components/DeleteProject.vue';
import NewPaygroup from '@/components/NewPaygroup.vue';
import { currency } from '@/assets/constants';
import Service from '@/service';

export default {
  name: 'App',
  components: {
    PayGroup,
    DarkToggle,
    NewProject,
    DeleteProject,
    NewPaygroup,
  },
  filters: {
    currency,
  },
  data: () => ({
    activeGroup: -1,
    project: null,
    projects: [],
    groups: [],
    groupSearch: '',
    service: Service,
  }),
  watch: {
    project() {
      this.activeGroup = -1;
      if (!this.project) return;
      this.getGroups();
      if (+this.$route.params.id !== +this.project) {
        this.$router.push({ params: { id: this.project } });
      }
    },
    groupSearch() {
      this.activeGroup = -1;
    },
    '$route.params.id': {
      immediate: true,
      handler() {
        this.project = +this.$route.params.id;
      },
    },
  },
  computed: {
    filteredGroups() {
      if (this.groupSearch) {
        const lowerGroupSearch = this.groupSearch.toLowerCase();
        return this.groups.filter((g) => g.name.toLowerCase().indexOf(lowerGroupSearch) === 0
                                      || g.name.toLowerCase().indexOf(` ${lowerGroupSearch}`) >= 0);
      }
      return this.groups;
    },
    sortedGroups() {
      return this.filteredGroups.slice().sort((a, b) => {
        if (a.name.toLowerCase() < b.name.toLowerCase()) {
          return -1;
        }
        return 1;
      });
    },
    totals() {
      const total = {
        liability: 0,
        asset: 0,
        balance: 0,
      };
      this.groups.forEach((group) => {
        const { payments } = group;
        payments.forEach((pay) => {
          total.liability += +pay.liability;
          total.asset += +pay.asset;
          if (+pay.liability !== 0) total.balance += +pay.liability - +pay.asset;
        });
      });
      return total;
    },
  },
  methods: {
    async getGroups() {
      if (!this.project) {
        this.groups = [];
        return;
      }
      const details = await this.service.getProjectDetails(this.project);
      this.groups = details.paygroups;
    },
    async getProjects() {
      this.projects = await this.service.getProjects();
    },
    setActiveGroup(groupId) {
      if (this.activeGroup === groupId) {
        this.activeGroup = -1;
      } else {
        this.activeGroup = groupId;
      }
    },
  },
  mounted() {
    this.getProjects();
  },
};
</script>
<style scoped>
.pay-group:nth-child(odd) {
  background:initial !important;
}
.pay-group.is-active ~ .pay-group:not(.is-active){
  opacity: 0.3;
}
</style>
