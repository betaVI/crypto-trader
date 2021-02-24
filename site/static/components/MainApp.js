export default {
    name: 'Main App',
    data() {
        return {
            wsconnection: null,
            product: {
                id:null,
                price:0
            },
            alertModel:{
                success: false,
                message: "",
                showalert: false
            }
        }
    },
    mounted(){
        this.fetchProducts();
    },
    beforeUnmount(){
        if (this.wsconnection){
            this.wsconnection.close();
        }
    },
    methods:{
        async fetchProducts(){
            console.log('Fetching products');
            const result = await fetch('/api/products', {method: "GET" });
            const data = await result.json();
            this.wsconnection = new WebSocket("wss://ws-feed.pro.coinbase.com");
            this.wsconnection.addEventListener('message', (event)=>{
                var response = JSON.parse(event.data);
                this.product = {
                    id: response.product_id,
                    price: response.price
                }
            });
            this.wsconnection.addEventListener('open', (event) => {
                this.wsconnection.send(JSON.stringify({
                    type: "subscribe",
                    product_ids: data.data,
                    channels: [ 'ticker' ]
                }));
                console.log('opened');
            });
            this.wsconnection.addEventListener('close', (event) => {
                console.log('closed');
                setTimeout(()=>{
                    this.fetchProducts()
                },5000);
            });
            this.wsconnection.addEventListener('error', (event) => {
                console.log('error: '+event)
            });
        },
        showAlert(alert){
            this.alertModel = alert;
        }
    },
    template:   `<alert-component :model=alertModel></alert-component>
                <div class="row">
                    <div class="col-xl-2 col-lg-3 col-md-4 col-sm-6">
                        <products-component :product="product" @showAlert=showAlert></products-component>
                    </div>
                    <div class="col-xl-6 col-lg-7 col-md-8 col-sm-6">
                    </div>
                    <div class="col-xl-4 col-lg-4 col-md-7 col-sm-6">
                        <account-component :product="product"></account-component>
                        <logs-component></logs-component>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-6 col-md-8">
                    </div>
                    <div class="col-lg-6 col-md-8">
                    </div>
                </div>`
}