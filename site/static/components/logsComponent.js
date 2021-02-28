export default{
    name: "LogsComponent",
    data(){
        return {
            isloading:false,
            logentries:[],
            pages:[],
            totallogcount:0,
            maxPages:1,
            pagesize:20,
            currentPage:1,
            currentSort:'createdat',
            currentSortDir: 'desc',
        }
    },
    mounted(){
        this.loadLogs();
    },
    methods:{
        async loadLogs(){
            this.isloading = true;
            const result = await fetch('/api/logs/'+this.pagesize+'/'+this.currentPage+'/'+this.currentSort+'/'+this.currentSortDir, { method: "GET"});
            const data = await result.json();
            this.totallogcount = data.totalcount;
            this.maxPages = Math.ceil(this.totallogcount/this.pagesize);
            this.logentries = data.data;
            this.setPages();
            this.isloading = false;
        },
        refresh(){
            this.loadLogs();
        },
        goToPage(page){
            this.currentPage=page;
            this.refresh();
        },
        previous(){
            this.currentPage--;
            this.refresh();
        },
        next(){
            this.currentPage++;
            this.refresh();
        },
        setPages(){
            this.pages=[1];
            var min = 2;
            var max = this.maxPages-1;
            if (max > 6){
                max = 5;
                if (this.currentPage>this.maxPages-4)
                    max = this.maxPages-1
                else if (this.currentPage>4)
                    max = this.currentPage+1;
                if (this.currentPage<5)
                    min=2;
                else
                    min = Math.min(this.currentPage-1, this.maxPages-4);
            }
            if (min > 3)
                this.pages.push('..');
            for (var x = min;x <= max;x++){
                this.pages.push(x);
            }
            if (max < this.maxPages-1)
                this.pages.push('..');
            if (this.maxPages > 1)
                this.pages.push(this.maxPages);
        },
        getLogLevel(loglevel){
            switch(loglevel){
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
                        <h4>
                            Logs
                            <loading-button-component class="btn-primary btn-sm" @click="refresh" :exloading=isloading>
                                <template #defaultLabel>
                                    <i class="fa fa-sync-alt"></i>
                                </template>
                            </loading-button-component>
                            <nav class="float-right">
                                <ul class="pagination pagination-sm">
                                    <li class="page-item" :class="{ disabled: currentPage == 1 }">
                                        <a class="page-link" @click="previous">
                                            <i class="fa fa-step-backward"></i>
                                        </a>
                                    </li>
                                    <li v-for="page in pages" class="page-item" :class="{ active: currentPage == page, disabled: page=='..' }" :style="{ cursor: page == '..' ? 'not-allowed': 'default' }">
                                        <a class="page-link" @click="goToPage(page)">
                                            {{ page }}
                                        </a>
                                    </li>
                                    <li class="page-item" :class="{ disabled: currentPage == maxPages }">
                                        <a class="page-link" @click="next">
                                            <i class="fa fa-step-forward"></i>
                                        </a>
                                    </li>
                                </ul>
                            </nav>
                        </h4>
                    </div> 
                    <div class="card-body">
                        <spinner-component :isloading="isloading"></spinner-component>
                        <table id="logs" class="table table-bordered table-sm" v-if="!isloading">
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Logger</th>
                                    <th>Message</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="log in logentries" :key="log.id" :class=getLogLevel(log.loglevelname)>
                                    <td class="column-fit">{{ log.createdat }}</td>
                                    <td class="column-fit">{{ log.loggername }}</td>
                                    <td>{{ log.message }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>`
}