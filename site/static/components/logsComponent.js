export default{
    name: "LogsComponent",
    data(){
        return {
            isloading:false,
            logentries:[],
            currentSort:'createdat',
            currentSortDir: 'desc',
            paginationModel:{
                pages:[],
                currentPage:1,
                pagesize:20,
                maxPages:1
            }
        }
    },
    methods:{
        getLogLevel(loglevelname){
            switch(loglevelname){
                case "DEBUG":
                    return 'table-default';
                case "INFO":
                    return 'table-info';
                case "WARNING":
                    return 'table-warning';
                case "ERROR":
                    return 'table-danger';
                case "CRITICAL":
                    return 'table-danger';
            }
        }
    },
    template:   `<div class="card">
                    <div class="card-header">
                        <h4>Logs</h4>
                    </div> 
                    <div class="card-body">
                        <api-table endpoint="/api/logs/" :columns="[{name:'Timestamp',class:'column-fit'},{name:'Logger',class:'column-fit'},{name:'Message'}]" v-slot:default="row">
                            <tr :class=getLogLevel(row.item.loglevelname)>
                                <td class="column-fit">{{ row.item.createdat }}</td>
                                <td class="column-fit">{{ row.item.loggername }}</td>
                                <td>{{ row.item.message }}</td>
                            </tr>
                        </api-table>
                    </div>
                </div>`
}