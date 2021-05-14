export default {
    name: 'Dashboard',
    data() {
        return {
            wsconnection: null,
            manualClose: false,
            product: {
                id:null,
                price:0
            }
        }
    },
    mounted(){
        this.manualClose = false;
        this.fetchProducts();
    },
    beforeUnmount(){
        this.manualClose = true;
        if (this.wsconnection){
            this.wsconnection.close();
        }
    },
    methods:{
        async fetchProducts(){
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
                if (!this.manualClose){
                    setTimeout(()=>{
                        this.fetchProducts()
                    },5000);
                }
            });
            this.wsconnection.addEventListener('error', (event) => {
                console.log('error: '+event)
            });
        }
    },
    template:   `<layout>
                    <div class="row">
                        <div class="col-xl-2 col-lg-3 col-md-4 col-sm-6">
                            <products-component :product="product"></products-component>
                        </div>
                        <div class="col-xl col-lg-7 col-md-8 col-sm-6">
                        </div>
                        <div class="col-xl-3 col-lg-3 col-md-6 col-sm-7">
                            <account-component :product="product"></account-component>
                            <productprofit></productprofit>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-lg-6 col-md-8">
                        </div>
                        <div class="col-lg-6 col-md-8">
                        </div>
                    </div>
                </layout>`
}