export default{
    name: "ProductsComponent",
    props: ["product"],
    watch:{
        product: function(product){
            for (var x = 0;x<this.traders.length; x++){
                if (this.traders[x].product==product.id){
                    this.traders[x].price = product.price;
                    break;
                }
            }
        }
    },
    data(){
        return {
            isloading:false,
            traders:[],
            tradermodel:{
                title:"",
                content:"",
                issubmitting:false,
                isloading:false,
            },
            alert: {
                success: false,
                message: "",
                showalert: false
            },
            modalAlert:{
                success: false,
                message: "",
                showalert: false
            }
        }
    },
    mounted(){
        this.fetchProducts();
    },
    methods:{
        async fetchProducts(){
            this.isloading = true;
            const result = await fetch('/api/traders', { method: "GET" });
            const data = await result.json();
            data.data.sort();
            this.traders = data.data;
            this.isloading = false;
        },
        async updateStatus(id, status, event){
            var content = JSON.stringify({ id: id, status: status });
            const result = await fetch('/api/traders/' + id + '/' + status, { method: "GET" });
            const data = await result.json();
            var trader = this.traders.find(t=>t.id == id);
            if (data.success && trader){
                trader.statusname = status;
            }
            this.showAlert(data.success, data.message)
        },
        async showCreateTrader(product){
            this.tradermodel.title = 'Create Trader';
            $(this.$refs.editmodal.$el).modal('show')
            this.tradermodel.content = await this.loadForm(0,product);
        },
        async showEditTrader(id){
            this.tradermodel.title = 'Edit Trader';
            $(this.$refs.editmodal.$el).modal('show')
            this.tradermodel.content = await this.loadForm(id);
        },
        showDeleteTrader(trader){
            this.deleteid = trader.id;
            this.tradermodel.title = 'Delete Trader'
            this.tradermodel.content = 'Are you sure you want to delete trader for ' + trader.product + '?';
            $(this.$refs.deletemodal.$el).modal('show')
        },
        async loadForm(id=0, product=null){
            this.tradermodel.content = "";
            this.tradermodel.isloading = true;
            var endpoint = '/form/traders';
            if (id != 0){
                endpoint += '?id=' + id;
            }
            if (product!=null){
                endpoint +='?product='+product;
            }
            const result  = await fetch(endpoint, { method: "GET" });
            this.tradermodel.isloading = false;
            return result.text();
        },
        async submitForm(){
            var form = $(this.$refs.editmodal.$el).find('form:first');
            this.tradermodel.issubmitting = true;
            try{
                const result = await fetch('/api/traders', {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: form.serialize()
                });
                const data = await result.json();
                if (data.success){
                    this.showAlert(data.success,data.message);
                    $(this.$refs.editmodal.$el).modal('hide');
                    this.fetchProducts();
                }
                else{
                    console.log(data.message);
                    if (data.message){
                        this.showModalAlert(false,data.message);
                    }
                    form.find("div[data-error]").remove();
                    for (const property in data.errors)
                        form.find('#'+ property).after('<div data-error class="text-danger">'+data.errors[property]+'</div>');
                }
            }
            catch(err){
                console.log('Failed to create trader: ' + err);
                this.showModalAlert(false, 'Exception: ' + err);
            }
            this.tradermodel.issubmitting = false;
        },
        async deleteTrader(){
            this.tradermodel.issubmitting = true;
            const result = await fetch('/api/traders/'+this.deleteid, { method: "DELETE" });
            const data = await result.json();
            $(this.$refs.deletemodal.$el).modal('hide');
            this.showAlert(data.success, data.message);
            if (data.success){
                this.fetchProducts();
            }
            this.tradermodel.issubmitting = false;
        },
        showAlert(success,message){
            this.alert.display = true;
            this.alert.success = success;
            this.alert.message = message;
        },
        showModalAlert(success,message){
            this.alert.display = true;
            this.alert.success = success;
            this.alert.message = message;
        },
        hasTrader(trader){
            return trader.statusname !== null;
        },
        isActive(statusname){
            return statusname=='Active';
        },
        isOutOfFunds(trader){
            if (trader.maxpurchaseamount && parseFloat(trader.totalspent) >= parseFloat(trader.maxpurchaseamount))
                return 'text-warning'
            return '';
        }
    },
    template:   `<alert-component :model=alert></alert-component>
                <spinner-component v-if="isloading"></spinner-component>
                <v-table v-if="!isloading" :columns="[{name:'Product'},{name:'Actions'}]" :rows="traders" v-slot:default="row">
                    <tr :class="isOutOfFunds(row.item)">
                        <td>{{ row.item.product }}<span class="badge badge-secondary float-right">{{ $filters.currencyUSD(row.item.price, 3) }}</span></td>
                        <td v-if="hasTrader(row.item)">
                            <loading-button-component v-if="row.item.statusname == 'Active'" class="btn-primary btn-sm" @click="updateStatus(row.item.id, 'Disabled')">
                                <template #defaultLabel>
                                    <i class="fa fa-pause"></i>
                                </template>
                            </loading-button-component>
                            <loading-button-component v-else-if="row.item.statusname == 'Disabled'" class="btn-primary btn-sm" @click="updateStatus(row.item.id, 'Active')">
                                <template #defaultLabel>
                                    <i class="fa fa-play"></i>
                                </template>
                            </loading-button-component>
                            <button type="button" class="btn btn-info btn-sm" @click="showEditTrader(row.item.id)">
                                <i class="fa fa-edit"></i>
                            </button>
                            <loading-button-component class="btn-danger btn-sm" @click="updateStatus(row.item.id, 'Cash Out')">
                                <template #defaultLabel>
                                    <i class="fa fa-money-bill-wave"></i>
                                </template>
                            </loading-button-component>
                        </td>
                        <td v-else>
                            <button type="button" class="btn btn-success btn-sm" data-id="0" @click="showCreateTrader(row.item.product)">
                                <i class="fa fa-plus"></i>
                            </button>
                        </td>
                    </tr>
                </v-table>
                <modal ref="deletemodal" @accepted="deleteTrader" :model=tradermodel :alertmodel=modalAlert>
                    <template v-slot:header>
                        <h5 class="modal-title">{{ tradermodel.title }}</h5>
                    </template>
                    <template v-slot:body>
                        <span v-html="tradermodel.content"></span>
                    </template>
                    <template v-slot:btnSubmit>
                        Confirm
                    </template>
                </modal>
                <modal ref="editmodal" @accepted="submitForm" :model=tradermodel :alertmodel=modalAlert>
                    <template v-slot:header>
                        <h5 class="modal-title">{{ tradermodel.title }}</h5>
                    </template>
                    <template v-slot:body>
                        <span v-html=tradermodel.content></span>
                    </template>
                </modal>`
}