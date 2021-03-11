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
            }
        },
    },
    data(){
        return {
            accountbalances: null,
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
            setTimeout(() => {
                this.loadPieGraph();
                this.isloading = false;
            }, 2000);
            setInterval(() => {
                this.updatePieGraph();
            }, 10000);
        },
        updatePieGraph(){
            if (this.accountbalances){
                var total = 0;
                for (var x=0; x<this.accounts.length;x++){
                    var account = this.accounts[x];
                    var balance = parseFloat(account.currencyvalue)* parseFloat(account.balance);
                    var index = this.accountbalances.data.labels.findIndex(l=>l.startsWith(account.currency));
                    if (index > -1){
                        this.accountbalances.data.datasets[0].data[index] = balance;
                    }
                    total+=balance;
                }
                this.accountbalances.options.title.text = "Account Balance "+ this.$filters.currencyUSD(total);
                this.accountbalances.update(0);
            }
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
                data.push(parseFloat((a.balance * a.currencyvalue).toFixed(2)));
                colors.push(dynamicColors());
            });

            var ctx = this.$refs.accountbalances.getContext('2d');
            var self = this;
            this.accountbalances = new Chart(ctx,{
                type:'pie',
                data:{
                    datasets:[{
                        data:data,
                        backgroundColor:colors
                    }],
                    labels:labels
                },
                options:{
                    title:{
                        display:true,
                        text:'Account Balances ' + this.$filters.currencyUSD(data.reduce((acc,val)=>acc+val))
                    },
                    tooltips: {
                        callbacks:{
                            label: function(toolTipItem, data){
                                var dataset = data.datasets[toolTipItem.datasetIndex];
                                var dataLabel = data.labels[toolTipItem.index];
                                var total = dataset.data.reduce(function(prevValue,currentValue, currentIndex, array){
                                    return prevValue+currentValue;
                                })
                                var value = dataset.data[toolTipItem.index];
                                var percent = ((value/total)*100).toFixed(2);
                                var newlabel = ': ' + self.$filters.currencyUSD(value)+' ' + percent+'%';
                                return dataLabel+newlabel;
                            }
                        }
                    }
                }
            })
        }
    },
    template:  `<spinner-component v-if="isloading"></spinner-component>
                <canvas ref="accountbalances" v-show="!isloading"/>`
}