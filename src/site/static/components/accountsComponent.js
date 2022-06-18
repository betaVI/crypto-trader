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
            isloading: false,
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
            var chart = null
            setTimeout(() => {
                chart = this.loadPieGraph();
                this.isloading = false;
            }, 2000);
            setInterval(() => {
                this.updatePieGraph(chart);
            }, 10000);
        },
        updatePieGraph(chart){
            if (chart){
                var total = 0;
                for (var x=0; x<this.accounts.length;x++){
                    var account = this.accounts[x];
                    var balance = parseFloat(account.currencyvalue)* parseFloat(account.balance);
                    var index = chart.data.labels.findIndex(l=>l.startsWith(account.currency));
                    if (index > -1){
                        chart.data.datasets[0].data[index] = balance;
                    }
                    total+=balance;
                }
                chart.options.plugins.title.text = "Account Balances "+ this.$filters.currencyUSD(total);
                chart.update('none');
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
            var graph = new Chart(ctx,{
                type:'pie',
                data:{
                    datasets:[{
                        data:data,
                        backgroundColor:colors,
                        borderColor:'#ddd',
                        borderWidth:1
                    }],
                    labels:labels
                },
                options:{
                    responsive:true,
                    aspectRatio:1.8,
                    maintainAspectRation: false,
                    plugins:{
                        title:{
                            display:true,
                            color: '#ddd',
                            fontSize:'18',
                            text:'Account Balances ' + this.$filters.currencyUSD(data.reduce((acc,val)=>acc+val))
                        },
                        legend:{
                            labels:{
                                color:'#ddd'
                            }
                        },
                        tooltip: {
                            callbacks:{
                                label: function(context){
                                    var dataset = context.dataset;
                                    var dataLabel = context.label;
                                    var total = dataset.data.reduce(function(prevValue,currentValue, currentIndex, array){
                                        return prevValue+currentValue;
                                    })
                                    var value =  context.parsed;
                                    var percent = ((value/total)*100).toFixed(2);
                                    var newlabel = ': ' + self.$filters.currencyUSD(value)+' ' + percent+'%';
                                    return dataLabel+newlabel;
                                }
                            }
                        }
                    }
                }
            })
            return graph;
        }
    },
    template:  `<spinner-component v-if="isloading"></spinner-component>
                <canvas ref="accountbalances" v-show="!isloading"/>`
}