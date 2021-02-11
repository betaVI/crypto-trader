export default{
    name: "TradersComponent",
    props: ['product'],
    data(){
        return {
            isloading: false,
            issubmitting: false,
            traders:[],
            modaltitle: "",
            modalcontent:"",
            modalcontentloading:false,
            alertsuccess: false,
            alertmessage: "",
            showalert: false,
            deleteid: 0
        };
    },
    watch: {
        product: function(product){
            for (var x = 0;x<this.traders.length; x++){
                if (this.traders[x].product==product.id){
                    this.traders[x].price = product.price;
                    break;
                }
            }
        },
    },
    mounted(){
        this.getTraders();
    },
    methods:{
        async getTraders(){
            this.isloading = true;
            const result  = await fetch('/api/traders', { method: "GET" });
            const data = await result.json();
            this.traders = data.data;
            this.isloading = false;
        },
        isActive(statusname){
            return statusname=='Active';
        },
        async showCreateTrader(){
            this.modaltitle = 'Create Trader';
            $(this.$refs.editmodal.$el).modal('show')
            this.modalcontent = await this.loadForm();
        },
        async showEditTrader(id){
            this.modaltitle = 'Edit Trader';
            $(this.$refs.editmodal.$el).modal('show')
            this.modalcontent = await this.loadForm(id);
        },
        showDeleteTrader(trader){
            this.deleteid = trader.id;
            this.modaltitle = 'Delete Trader'
            this.modalcontent = 'Are you sure you want to delete ' + trader.product + '?';
            $(this.$refs.deletemodal.$el).modal('show')
        },
        async deleteTrader(){
            this.issubmitting = true;
            const result = await fetch('/api/traders/'+this.deleteid, { method: "DELETE" });
            const data = await result.json();
            if (data.success){
                $(this.$refs.deletemodal.$el).modal('hide')
                this.getTraders();
            }
            else{
                if (data.message){
                    this.showAlert(false,data.message);
                }
            }
            this.issubmitting = false;
        },
        async submitForm(){
            var form = $(this.$refs.editmodal.$el).find('form:first');
            this.issubmitting = true;
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
                    $(this.$refs.editmodal.$el).modal('hide');
                    this.getTraders();
                }
                else{
                    if (data.message){
                        this.showAlert(false,data.message);
                    }
                    form.find("div[data-error]").remove();
                    for (const property in data.errors)
                        form.find('#'+ property).after('<div data-error class="text-danger">'+data.errors[property]+'</div>');
                }
            }
            catch(err){
                console.log('Failed to create trader: ' + err);
            }
            this.issubmitting = false;
        },
        showAlert(success,message){
            this.showalert = true;
            this.alertsuccess = success;
            this.alertmessage = message;
        },
        async loadForm(id=0){
            this.modalcontent = "";
            this.modalcontentloading = true;
            var endpoint = '/form/traders';
            if (id != 0){
                endpoint += '/' + id;
            }
            const result  = await fetch(endpoint, { method: "GET" });
            this.modalcontentloading = false;
            return result.text();
        }
    },
    template:   `<div class="card">
                    <div class="card-header">
                        <h4>Traders<button type="button" class="btn btn-success float-right" data-id="0" @click="showCreateTrader()">Add</button></h4>
                    </div>
                    <div class="card-body">
                        <div class="d-flex justify-content-center" v-if="isloading">
                            <div class="spinner-border text-primary" role="status">
                                <span class="sr-only">Loading...</span>
                            </div>
                        </div>
                        <table id="traders" class="table table-striped table-bordered table-sm" style="width: 100%;" v-if="!isloading">
                            <thead>
                                <tr>
                                    <th>Status</th>
                                    <th>Product</th>
                                    <th>BUY Upper/Lower</th>
                                    <th>Sell Upper/Lower</th>
                                    <th data-orderable="false">&nbsp;</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in traders" :key="item.id" :data-product="item.product">
                                    <td class="align-middle"><span class="badge" :class="isActive(item.statusname) ? 'badge-success' : 'badge-danger'">{{ item.statusname }}</span></td>
                                    <td class="align-middle" data-product>{{ item.product }}<span class="badge badge-secondary float-right">{{ $filters.currencyUSD(item.price) }}</span></td>
                                    <td class="align-middle">{{ item.buyupperthreshold + ' / ' + item.buylowerthreshold }}</td>
                                    <td class="align-middle">{{ item.sellupperthreshold + ' / ' + item.selllowerthreshold }}</td>
                                    <td class="align-middle column-fit">
                                        <button type="button" class="btn btn-primary btn-sm" @click="showEditTrader(item.id)">
                                            <i class="fa fa-edit"></i>
                                        </button>
                                        <button type="button" class="btn btn-danger btn-sm" @click="showDeleteTrader(item)">
                                            <i class="fa fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <delete-trader-modal ref="deletemodal" @accepted="deleteTrader" :issubmitting="issubmitting">
                    <template v-slot:header>
                        <h5 class="modal-title">{{ modaltitle }}</h5>
                    </template>
                    <template v-slot:body>
                        <span v-html="modalcontent"></span>
                    </template>
                    <template v-slot:btnSubmit>
                        Confirm
                    </template>
                </delete-trader-modal>
                <edit-trader-modal ref="editmodal" @accepted="submitForm" :issubmitting="issubmitting" :alertsuccess="alertsuccess" :alertmessage="alertmessage" :showalert="showalert" :modalcontentloading="modalcontentloading">
                    <template v-slot:header>
                        <h5 class="modal-title">{{ modaltitle }}</h5>
                    </template>
                    <template v-slot:body>
                        <span v-html="modalcontent"></span>
                    </template>
                </edit-trader-modal>`
}