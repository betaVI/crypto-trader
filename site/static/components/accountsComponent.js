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
                        <v-table :columns="['Currency','Quantity','Price','Balance']" :rows=accounts v-slot:default="row">
                            <tr>
                                <td class="column-fit">{{ row.item.currency }}</td>
                                <td class="text-right">{{ $filters.decimal(row.item.balance, 5) }}</td>
                                <td class="text-right">{{ $filters.currencyUSD(row.item.currencyvalue, 5) }}</td>
                                <td class="text-right">{{ $filters.currencyUSD(row.item.balance * row.item.currencyvalue, 2) }}</td>
                            </tr>
                        </v-table>
                    </div>
                </div>`
}