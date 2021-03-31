export default{
    name: "LogsComponent",
    data(){
        return {
            logentries:[],
            currentSort:'createdat',
            currentSortDir: 'desc',
            paginationModel:{
                pages:[],
                currentPage:1,
                pagesize:20,
                maxPages:1
            },
            columns: [
                {
                    name:'Timestamp',
                    class:'column-fit',
                    type:Date,
                    filter:{
                        type:'range',
                        value:'',
                        low:{
                            text:'Start Date'
                        },
                        high:{
                            text:'End Date'
                        }
                    }
                    
                },
                {
                    name:'Logger',
                    class:'column-fit',
                    filter:{
                        type:'dropdown',
                        value:'',
                        choices:[]
                    }
                },
                {
                    name:'Message'
                }
            ]
        }
    },
    mounted(){
        this.getLoggers();
    },
    methods:{
        async getLoggers(){
            const result = await fetch('/api/loggers', { method: "GET" });
            const data = await result.json()
            if (data.success){
                var column = this.columns.find(c=>c.name == 'Logger');
                if (column){
                    column.filter.choices.push({text:'Any', value:''})
                    data.data.forEach(l => {
                        column.filter.choices.push({text: l.loggername, value: l.loggername});
                    });
                }
            }
        },
        getLogLevel(loglevelname){
            switch(loglevelname){
                case "DEBUG":
                    return 'text-default';
                case "INFO":
                    return 'text-info';
                case "WARNING":
                    return 'text-warning';
                case "ERROR":
                    return 'text-danger';
                case "CRITICAL":
                    return 'table-critical';
            }
        }
    },
    template:   `<div class="card">
                    <div class="card-header">
                        <h4>Logs</h4>
                    </div> 
                    <div class="card-body">
                        <api-table endpoint="/api/logs/" filtertitle="Log filter" :columns="columns" v-slot:default="row">
                            <tr :class=getLogLevel(row.item.loglevelname)>
                                <td class="column-fit">{{ row.item.createdat }}</td>
                                <td class="column-fit">{{ row.item.loggername }}</td>
                                <td>{{ row.item.message }}</td>
                            </tr>
                        </api-table>
                    </div>
                </div>`
}