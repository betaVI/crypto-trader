export default{
    name: 'ProfitComponent',
    data(){
        return {
            data: [],
            isloading:false,
            productprofit: null,
            alertModel:{
                display:false,
                success:true,
                message:''
            }
        }
    },
    mounted(){
        this.loadData();
    },
    methods:{
        async loadData(){
            this.isloading = true;
            try{
                const result = await fetch('/api/reports/profit', { method: "GET" });
                const data = await result.json();
                if (data.success){
                    if (this.data.length>0){
                        data.data.forEach(d=>{
                            var product = this.data.find(p=>p.product == d.product);
                            if (product){
                                product.netprofit = d.netprofit;
                                product.grossprofit = d.grossprofit;
                            }
                        });
                        this.productprofit.update(0);
                    }
                    else{
                        this.data = data.data;
                        this.initializeGraph();
                    }
                }
                else
                    this.displayAlert(data.success,data.message);
            }
            catch(error){
                this.displayAlert(false, 'Failed to load data: ' + error);
            }
            this.isloading = false;
        },
        initializeGraph(){
            var dynamicColors = function() {
                var r = Math.floor(Math.random() * 255);
                var g = Math.floor(Math.random() * 255);
                var b = Math.floor(Math.random() * 255);
                return "rgb(" + r + "," + g + "," + b + ")";
            };
            var colors =[];
            var data = [];
            var labels = [];

            this.data.forEach(p=>{
                labels.push(p.product);
                data.push(p.grossprofit);
                colors.push(dynamicColors());
            });
            
            var ctx = this.$refs.productprofit.getContext('2d');
            var self = this;
            this.productprofit = new Chart(ctx,{
                type:'horizontalBar',
                data:{
                    datasets:[{
                        data:data,
                        backgroundColor:colors,
                        // borderColor:'#ccc',
                        borderWidth:1
                    }],
                    labels:labels
                },
                options:{
                    title:{
                        display:true,
                        fontColor: '#ccc',
                        fontSize:'18',
                        text:'Product Profitability'
                    },
                    legend:{
                        labels:{
                            fontColor:'#ccc'
                        }
                    }
                }
            })

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