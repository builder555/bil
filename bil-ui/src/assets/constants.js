/* eslint-disable import/prefer-default-export */
export const baseUrl = `${window.location.protocol}//${window.location.hostname}`
                     + `${process.env.NODE_ENV === 'development' ? ':8888/apps/bil' : ''}/main.php`;

const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
});

export const currency = (value) => {
  if (!Number.isNaN(Number.parseFloat(value))) {
    return formatter.format(value);
  }
  return value;
};
