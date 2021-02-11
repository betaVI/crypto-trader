export default {
    name: 'Main App',
    data() {
        return {
            wsconnection: null,
            product: {
                id:null,
                price:0
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
                if (response.side=="buy"){
                    this.product = {
                        id: response.product_id,
                        price: response.price
                    }
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
            this.wsconnection.addEventListener('close', function(event){
                console.log('closed');
            });
            this.wsconnection.addEventListener('error', (event) => {
                console.log('error: '+event)
                setTimeout(()=> this.fetchProducts(),5000);
            });
        }
    },
    template:   `<div class="row">
                    <div class="col-xl-2 col-lg-3 col-md-4 col-sm-6">
                        <products-component :product="product"></products-component>
                    </div>
                    <div class="col-xl-5 col-lg-6 col-md-8 col-sm-6">
                        <traders-component :product="product"></traders-component>
                        <account-component :product="product"></account-component>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-6 col-md-8">
                    </div>
                    <div class="col-lg-6 col-md-8">
                    </div>
                </div>`
}