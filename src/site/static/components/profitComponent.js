export default{
    name: 'ProfitComponent',
    data(){
        return {
            data: [],
            dates: [],
            isloading:false,
            timer: null,
            alertModel:{
                display:false,
                success:true,
                message:''
            }
        }
    },
    mounted(){
        this.initialize();
    },
    unmounted(){
        if (this.timer!=null){
            clearInterval(this.timer);
        }
    },
    methods:{
        async initialize(){
            var chart = null;
            this.isloading = true;
            await this.loadData((data)=>{
                this.data = data.data;
                this.dates = data.dates; 
                chart = this.initializeGraph();
                this.isloading = false;
                this.timer = setInterval(() => {
                    this.updateGraph(chart);
                }, 10000);
            })
        },
        async updateGraph(chart){
            self = this;
            await this.loadData((data)=>{
                data.data.forEach(d=>{
                    var product = self.data.find(p=>p.product == d.product);
                    if (product){
                        product.netprofit = d.netprofit;
                        product.grossprofit = d.grossprofit;
                    }
                });
                chart.update('none');
            })
        },
        async loadData(onsuccess){
            try{
                const result = await fetch('/api/reports/profit', { method: "GET" });
                const data = await result.json();
                if (data.success){
                    onsuccess(data);
                }
                else
                    this.displayAlert(data.success,data.message);
            }
            catch(error){
                this.displayAlert(false, 'Failed to load data: ' + error);
            }
        },
        initializeGraph(){
            var dynamicColors = function() {
                var r = Math.floor(Math.random() * 255);
                var g = Math.floor(Math.random() * 255);
                var b = Math.floor(Math.random() * 255);
                return "rgb(" + r + "," + g + "," + b + ")";
            };
            var datasets=[]

            this.data.forEach(p=>{
                datasets.push({
                    label: p.product,
                    data: p.values,
                    backgroundColor:dynamicColors(),
                    borderWidth:1
                })
            });
            
            var ctx = this.$refs.productprofit.getContext('2d');
            var self = this;
            var chart = new Chart(ctx,{
                type:'bar',
                data:{
                    datasets:datasets,
                    labels:this.dates
                },
                options:{
                    plugins:{
                        title:{
                            display:true,
                            color: '#fff',
                            size:'24',
                            text:'Product Profitability'
                        },
                        tooltip: {
                            callbacks:{
                                title: function(context){
                                    var label = context[0].label;
                                    var total = context.reduce(function(sum,currentValue, currentIndex, array){
                                        return parseFloat(sum)+parseFloat(currentValue.raw);
                                    }, 0);
                                    return label +' - '+ self.$filters.currencyUSD(total);
                                },
                                label: function(context){
                                    var dataset = context.dataset;
                                    var value = dataset.data[context.dataIndex];
                                    var label = dataset.label;
                                    return label + ': ' + self.$filters.currencyUSD(value);
                                }
                            }
                        }
                    },
                    scales:{
                        x:{
                            stacked:true,
                            grid:{
                                display:false
                            }
                        },
                        y:{
                            stacked:true,
                        }
                    },
                }
            })
            return chart;
        },
        displayAlert(success,message){
            this.alertModel.display = true;
            this.alertModel.success = success;
            this.alertModel.message = message;
        }
    },
    template:   `<alert-component :model=alertModel></alert-component>
                <spinner-component v-if="isloading"></spinner-component>
                <canvas ref="productprofit" v-show="!isloading"/>`
}