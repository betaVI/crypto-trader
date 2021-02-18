import SpinnerComponent from './spinnerComponent.js';
import accountsComponent from './accountsComponent.js';
import modalComponent from './modalComponent.js';
import loadingButtonComponent from './loadingButtonComponent.js';
import alertComponent from './alertComponent.js';
import productsComponent from './productsComponent.js';
import mainApp from './MainApp.js';
import spinnerComponent from './spinnerComponent.js';

const app = Vue.createApp(mainApp);
app.config.globalProperties.$filters = {
    currencyUSD(value, decimalplaces){
        var currencyFormat = new Intl.NumberFormat('en-US',options={ minimumFractionDigits: decimalplaces, style: 'currency', currency: 'USD' });
        return currencyFormat.format(value);
    },
    decimal(value, decimalplaces){
        var currencyFormat = new Intl.NumberFormat('en-US',options={ minimumFractionDigits: decimalplaces });
        return currencyFormat.format(value);
    }
};
app.component("loading-button-component", loadingButtonComponent)
app.component("alert-component", alertComponent);
app.component("spinner-component", spinnerComponent);
app.component("products-component", productsComponent);
app.component("account-component", accountsComponent);
app.component("trader-modal", modalComponent);
app.mount('#mainContent');