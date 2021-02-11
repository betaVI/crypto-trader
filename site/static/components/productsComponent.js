export default{
    name: "ProductsComponent",
    props: ["product"],
    watch:{
        product: function(product){
            for (var x = 0;x<this.products.length; x++){
                if (this.products[x].id==product.id){
                    this.products[x].price = product.price;
                    break;
                }
            }
        }
    },
    data(){
        return {
            isloading: false,
            products:[]
        }
    },
    mounted(){
        this.fetchProducts();
    },
    methods:{
        async fetchProducts(){
            this.isloading = true;
            const result = await fetch('/api/products', { method: "GET" });
            const data = await result.json();
            data.data.sort();
            for (var x=0;x<data.data.length;x++)
                this.products.push({ id: data.data[x], price:0 })
            this.isloading = false;
        }
    },
    template:   `<div class="card">
                    <div class="card-header">
                        <h4>Products</h4>
                    </div>
                    <div class="card-body">
                        <spinner-component :isloading="isloading"></spinner-component>
                        <table class="table table-striped table-bordered table-sm" v-if="!isloading">
                            <thead>
                                <tr>
                                    <th>Product</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="product in products" :key="product.id">
                                    <td>{{ product.id }}<span class="badge badge-secondary float-right">{{ $filters.currencyUSD(product.price) }}</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>`
}