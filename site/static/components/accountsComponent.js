export default {
    name: "AccountsComponent",
    props: ['product'],
    watch: {
        product: function(product){
            if (!product || !product.id){
                return;
            }
            var currency = product.id.substring(0, product.id.indexOf('-'));
            var account = this.accounts.find(a=>a.currency == currency);
            if (account){
                account.currencyvalue = product.price;
                var balance = parseFloat(account.currencyvalue)* parseFloat(account.balance);
                if (this.piechart){
                    var index = this.piechart.data.labels.indexOf(currency);
                    if (index > 0){
                        console.log(balance);
                        this.piechart.data.datasets[0].data[index] = balance;
                    }
                    this.piechart.update(0);
                }
                var total = 0;
                for (var x = 0;x<this.accounts.length; x++){
                    total += parseFloat(this.accounts[x].currencyvalue)* parseFloat(this.accounts[x].balance);
                }
                this.accountbalance = total;
            }
        },
    },
    data(){
        return {
            piechart: null,
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
            this.loadPieGraph();
            this.isloading = false;
        },
        loadPieGraph(){
            var dynamicColors = function() {
                var r = Math.floor(Math.random() * 255);
                var g = Math.floor(Math.random() * 255);
                var b = Math.floor(Math.random() * 255);
                return "rgb(" + r + "," + g + "," + b + ")";
            };
            var colors =[];
            var data = [];
            var labels = [];
            this.accounts.forEach((a)=>{
                labels.push(a.currency);
                data.push(a.balance * a.currencyvalue);
                colors.push(dynamicColors());
            });

            var ctx = document.getElementById('piegraph').getContext('2d');
            this.piechart = new Chart(ctx,{
                type:'pie',
                data:{
                    datasets:[{
                        data:data,
                        backgroundColor:colors
                    }],
                    labels:labels
                },
                options:{

                }
            })
        }
    },
    template:  `<div class="card">
                    <div class="card-header">
                        <h4>Accounts<span id="lblTotalPortfolio" class="float-right">{{ $filters.currencyUSD(accountbalance, 2) }}</span></h4>
                    </div>
                    <div class="card-body">
                        <spinner-component v-if="isloading"></spinner-component>
                        <v-table v-if="!isloading" :columns="[{name:'Currency',class:'column-fit'},{name:'Quantity',class:'text-right'},{name:'Price',class:'text-right'},{name:'Balance',class:'text-right'}]" :rows=accounts v-slot:default="row">
                            <tr>
                                <td class="column-fit">{{ row.item.currency }}</td>
                                <td class="text-right">{{ $filters.decimal(row.item.balance, 5) }}</td>
                                <td class="text-right">{{ $filters.currencyUSD(row.item.currencyvalue, 5) }}</td>
                                <td class="text-right">{{ $filters.currencyUSD(row.item.balance * row.item.currencyvalue, 2) }}</td>
                            </tr>
                        </v-table>
                        <canvas id="piegraph"/>
                    </div>
                </div>`
}