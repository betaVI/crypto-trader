export default {
    name: "AccountsComponent",
    props: ['product'],
    watch: {
        product: function(product){
            if (!product || !product.id){
                return;
            }
            var currency = product.id.substring(0, product.id.indexOf('-'));
            var total = 0;
            for (var x = 0;x<this.accounts.length; x++){
                if (this.accounts[x].currency==currency){
                    this.accounts[x].currencyvalue = product.price;
                }
                total += parseFloat(this.accounts[x].currencyvalue)* parseFloat(this.accounts[x].balance);
            }
            this.accountbalance = total;
        },
    },
    data(){
        return {
            isloading: false,
            accountbalance: 0,
            accounts: []
        };
    },
    mounted(){
        this.getAccounts();
    },
    methods:{
        async getAccounts(){
            this.isloading=true;
            const result = await fetch('/api/accounts',{
                method:"GET"
            });
            const data = await result.json();
            this.accounts = data.data;
            this.isloading = false;
        }
    },
    template:  `<div class="card">
                    <div class="card-header">
                        <h4>Accounts<span id="lblTotalPortfolio" class="float-right">{{ $filters.currencyUSD(accountbalance, 2) }}</span></h4>
                    </div>
                    <div class="card-body">
                        <spinner-component :isloading="isloading"></spinner-component>
                        <table id="accounts" class="table table-striped table-bordered table-sm" v-if="!isloading">
                            <thead>
                                <tr>
                                    <th>Currency</th>
                                    <th>Quantity</th>
                                    <th>Price</th>
                                    <th>Balance</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="account in accounts" :key="account.currency" :data-currency="account.currency">
                                    <td class="column-fit">{{ account.currency }}</td>
                                    <td>{{ $filters.decimal(account.balance, 5) }}</td>
                                    <td>{{ $filters.currencyUSD(account.currencyvalue, 5) }}</td>
                                    <td>{{ $filters.currencyUSD(account.balance * account.currencyvalue, 2) }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>`
}