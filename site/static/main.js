import accountsComponent from './components/accountsComponent.js';
import modalComponent from './components/modalComponent.js';
import loadingButtonComponent from './components/loadingButtonComponent.js';
import alertComponent from './components/alertComponent.js';
import productsComponent from './components/productsComponent.js';
import spinnerComponent from './components/spinnerComponent.js';
import logsComponent from './components/logsComponent.js';
import routeLinkComponent from './components/routeLinkComponent.js';
import router from './navigation/router.js'
import layouttemplate from './components/layouttemplate.js';
import tableComponent from './components/tableComponent.js';
import paginationComponent from './components/paginationComponent.js';
import ordersComponent from './components/ordersComponent.js';
import apiTableComponent from './components/apiTableComponent.js';

const app = Vue.createApp(router);
app.config.productionTip = false;
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
app.component("api-table", apiTableComponent);
app.component("v-paging", paginationComponent);
app.component("v-table", tableComponent);
app.component("layout", layouttemplate);
app.component("router-link", routeLinkComponent);
app.component("orders-component", ordersComponent);
app.component("loading-button-component", loadingButtonComponent);
app.component("alert-component", alertComponent);
app.component("spinner-component", spinnerComponent);
app.component("products-component", productsComponent);
app.component("logs-component", logsComponent)
app.component("account-component", accountsComponent);
app.component("modal", modalComponent);
app.mount('#mainContent');