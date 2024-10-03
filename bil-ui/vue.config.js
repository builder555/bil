module.exports = {
  transpileDependencies: [
    'vuetify',
  ],
  devServer: {
    disableHostCheck: true,
    host: '0.0.0.0',
    // public: '0.0.0.0:8081',
    // https: true
  },
  // publicPath: '',
  // publicPath: `${process.env.NODE_ENV === 'development' ? '' : '/bil/'}`,
};
