import SpinnerComponent from './spinnerComponent.js';
import AccountsComponent from './accountsComponent.js';
import TradersComponent from './tradersComponent.js';
import ModalComponent from './modalComponent.js';
import ProductsComponent from './productsComponent.js';
import MainApp from './MainApp.js';

var currencyFormat = new Intl.NumberFormat('en-US',options={ minimumFractionDigits: 2, style: 'currency', currency: 'USD' });
const app = Vue.createApp(MainApp);
app.config.globalProperties.$filters = {
    currencyUSD(value){
        return currencyFormat.format(value);
    }
};
app.component("spinner-component", SpinnerComponent);
app.component("products-component", ProductsComponent);
app.component("account-component", AccountsComponent);
app.component("traders-component", TradersComponent);
app.component("edit-trader-modal", ModalComponent);
app.component("delete-trader-modal", ModalComponent);
app.mount('#mainContent');