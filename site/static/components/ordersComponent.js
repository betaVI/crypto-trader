export default{
    name: "Order Component",
    data(){
        return {
            columns:[
                {
                    name:'Timestamp',
                    class:'column-fit',
                    type:Date,
                    filter:{
                        value:''
                    }
                },
                {
                    name:'Product',
                    class:'column-fit',
                    filter:{
                        type:'dropdown',
                        value:'',
                        choices:[]
                    }
                },
                {
                    name:'Funds',
                    class:'text-right'
                },
                {
                    name:'Size',
                    class:'text-right'
                },
                {
                    name:'Price',
                    class:'text-right'
                },
                {
                    name:'Fee',
                    class:'text-right'
                }
            ]
        }
    },
    mounted(){
        this.loadProducts();
    },
    methods:{
        async loadProducts(){
            const result = await fetch('/api/orders/products', { method: "GET" });
            const data = await result.json()
            if (data.success){
                var column = this.columns.find(c=>c.name=='Product');
                if (column){
                    column.filter.choices.push({ text:"Any", value:''});
                    data.data.forEach(p=>{
                        column.filter.choices.push({ text: p.name, value: p.name});
                    })
                }
            }
        },
        getSide(side){
            return side=='sell'?'table-success':'table-danger';
        },
    },
    template:   `<div class="card">
                    <div class="card-header">
                        <h4>Orders</h4>
                    </div> 
                    <div class="card-body">
                        <api-table endpoint="/api/orders/" filtertitle="Order filter" :columns=columns v-slot:default="row">
                            <tr :class=getSide(row.item.side)>
                                <td class="column-fit">{{ row.item.createdat }}</td>
                                <td class="column-fit">{{ row.item.product }}</td>
                                <td class="text-right">{{ $filters.currencyUSD(row.item.funds, 2) }}</td>
                                <td class="text-right">{{ $filters.decimal(row.item.size, 7) }}</td>
                                <td class="text-right">{{ $filters.currencyUSD(row.item.price, 5) }}</td>
                                <td class="text-right">{{ $filters.currencyUSD(row.item.fee, 5) }}</td>
                            </tr>
                        </api-table>
                    </div>
                </div>`
}