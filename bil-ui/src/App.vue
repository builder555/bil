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
      <DeleteProject v-if="project" :project="project" @deleted="onProjectDeleted()" />
      <NewProject v-else @created="getProjects()"/>
      <DarkToggle/>
    </v-app-bar>
    <v-main v-if="project">
      <v-container>
        <v-row>
          <v-col cols="12" sm="6" md="8">
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="searchStartDate"
                  label="Start Date"
                  placeholder="YYYY-MM-DD"
                  v-mask="'####-##-##'"
                  inputmode="numeric"
                  clearable
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="searchEndDate"
                  label="End Date"
                  placeholder="YYYY-MM-DD"
                  v-mask="'####-##-##'"
                  inputmode="numeric"
                  clearable
                />
              </v-col>
            </v-row>
            <v-row class="ma-0 pa-0">
              <v-col cols="12" class="ma-0 pa-0">
                <ProjectHistory :project="project"/>
              </v-col>
            </v-row>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <GroupTotals :totals="totals" />
          </v-col>
        </v-row>
        <v-row class="ma-0 pa-0 mx-sm-n3">
          <v-col cols="12" sm="6"  class="ma-0 pa-0">
            <v-text-field class="ma-0 pa-0 mr-sm-3"
              v-model="groupSearch"
              label="Search groups"
              clearable
            />
          </v-col>
          <v-col cols="12" sm="6" class="ma-0 pa-0">
            <v-text-field class="ma-0 pa-0"
              v-model="paymentSearch"
              label="Search Payments"
              clearable
            />
          </v-col>
        </v-row>
        <v-row class="indigo darken-1 white--text">
          <v-col
            cols="12"
            sm="6"
            class="text-left"
          >
            Payment Group
            <NewPaygroup
              :project="project"
              @created="getGroups"
            />
          </v-col>
          <v-col cols="4" sm="2" class="text-right">Balance</v-col>
          <v-col cols="4" sm="2" class="text-right">Owed</v-col>
          <v-col cols="4" sm="2" class="text-right">Paid</v-col>
        </v-row>
        <PayGroup
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
import { mask } from 'vue-the-mask';
import PayGroup from './components/PayGroup.vue';
import DarkToggle from './components/DarkToggle.vue';
import NewProject from './components/NewProject.vue';
import DeleteProject from './components/DeleteProject.vue';
import NewPaygroup from './components/NewPaygroup.vue';
import GroupTotals from './components/GroupTotals.vue';
import ProjectHistory from './components/ProjectHistory.vue';
import { currency } from './assets/constants';
import Service from './service';

export default {
  name: 'App',
  components: {
    DarkToggle,
    DeleteProject,
    GroupTotals,
    NewPaygroup,
    NewProject,
    PayGroup,
    ProjectHistory,
  },
  directives: { mask },
  filters: {
    currency,
  },
  data: () => ({
    activeGroup: -1,
    historyState: null,
    project: null,
    projects: [],
    rawGroups: [],
    groupSearch: '',
    paymentSearch: '',
    service: Service,
    searchStartDate: '',
    searchEndDate: '',
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
    historyState() {
      this.getGroups();
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
    '$route.params.state': {
      immediate: true,
      handler() {
        this.historyState = this.$route.params.state;
      },
    },
  },
  computed: {
    groups() {
      let filteredGroups = JSON.parse(JSON.stringify(this.rawGroups));
      if (this.groupSearch) {
        const escapedSearch = this.groupSearch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(?<![A-Za-z])${escapedSearch}`, 'gi');
        filteredGroups = filteredGroups.filter((g) => !!g.name?.match(regex));
      }
      if (this.searchStartDate || this.searchEndDate || this.paymentSearch) {
        filteredGroups = filteredGroups.filter((group) => group.payments.length > 0);
      }

      filteredGroups.forEach((group) => {
        if (this.searchStartDate?.length >= 10) {
          group.payments = group.payments.filter((pay) => new Date(pay.date) >= new Date(this.searchStartDate));
        }
        if (this.searchEndDate?.length >= 10) {
          group.payments = group.payments.filter((pay) => new Date(pay.date) <= new Date(this.searchEndDate));
        }
        if (this.paymentSearch) {
          const escapedSearch = this.paymentSearch.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const regex = new RegExp(`(?<![A-Za-z])${escapedSearch}`, 'gi');
          group.payments = group.payments.filter((pay) => !!pay.name?.match(regex));
        }
      });
      return filteredGroups;
    },
    sortedGroups() {
      return this.groups.slice().sort((a, b) => {
        if (a.name.toLowerCase() < b.name.toLowerCase()) {
          return -1;
        }
        return 1;
      });
    },
    totals() {
      const total = {
        owed: 0,
        paid: 0,
        balance: 0,
      };
      this.groups.forEach((group) => {
        const { payments } = group;
        let groupBalance = 0;
        let groupPaid = 0;
        let groupOwed = 0;
        payments.forEach((pay) => {
          groupOwed += +pay.owed;
          groupPaid += +pay.paid;
        });
        groupBalance += groupOwed - groupPaid;
        // only count groups that have "owed" and "paid" values
        if (Math.round(groupOwed * 100000000) !== 0) total.balance += groupBalance;
        total.owed += groupOwed;
        total.paid += groupPaid;
      });
      return total;
    },
  },
  methods: {
    async getGroups() {
      if (!this.project) {
        this.rawGroups = [];
        return;
      }
      const details = await this.service.getProjectDetails(this.project, this.historyState);
      this.rawGroups = details.paygroups;
    },
    async getProjects() {
      const projects = await this.service.getProjects();
      this.projects = projects.sort((a, b) => {
        if (a.name.toLowerCase() < b.name.toLowerCase()) {
          return -1;
        }
        return 1;
      });
    },
    setActiveGroup(groupId) {
      if (this.activeGroup === groupId) {
        this.activeGroup = -1;
      } else {
        this.activeGroup = groupId;
      }
    },
    async onProjectDeleted() {
      await this.getProjects();
      this.project = null;
    },
  },
  async mounted() {
    await this.getProjects();
  },
};
</script>
<style scoped>
.pay-group:nth-child(odd) {
  background: initial !important;
}

.pay-group.is-active~.pay-group:not(.is-active) {
  opacity: 0.3;
}
</style>
