import Vue from 'vue';
import Vuetify from 'vuetify/lib';
import colors from 'vuetify/lib/util/colors';
import VuetifyConfirm from 'vuetify-confirm';

Vue.use(Vuetify);

const vuetify = new Vuetify({
  icons: {
    iconfont: 'fa',
  },
  theme: {
    themes: {
      light: {
        accent: colors.lightBlue.lighten5,
        secondary: colors.blueGrey.lighten5,
      },
      dark: {
        accent: colors.grey.darken4,
        secondary: colors.blueGrey.darken4,
      },
    },
  },
});
Vue.use(VuetifyConfirm, { vuetify });

export default vuetify;
