export default{
    name: "API Table",
    props: ['endpoint', 'columns'],
    data(){
        return {
            rows:[],
            // columns:[],
            isloading:false,
            currentSort:'createdat',
            currentSortDir: 'desc',
            paginationModel:{
                pages:[],
                currentPage:1,
                pagesize:20,
                maxPages:1
            },
            alertModel:{
                success: false,
                message: "",
                display: false
            }
        }
    },
    mounted(){
        this.loadTable();
    },
    methods:{
        showAlert(message, success = true){
            this.alertModel.display=true;
            this.alertModel.message = message;
            this.alertModel.success = success;
        },
        async loadTable(){
            this.isloading = true;
            try{
                const result = await fetch(this.endpoint+this.paginationModel.pagesize+'/'+this.paginationModel.currentPage+'/'+this.currentSort+'/'+this.currentSortDir, { method: "GET"});
                const data = await result.json();
                if (data.success){
                    this.paginationModel.maxPages = Math.ceil(data.totalcount/this.paginationModel.pagesize);
                    this.rows = data.data;
                    // if (this.rows.length>0){
                    //     Object.keys(this.rows[0]).forEach(function(key){
                    //         console.log(key);
                    //         this.columns.push(key);
                    //     })
                    // }                        
                    this.setPages();
                }
                else
                    this.showAlert(data.message,data.success);
            }
            catch(error){
                this.showAlert("Failed to load data: " +error, false);
            }
            this.isloading = false;
        },
        refresh(){
            this.loadTable();
        },
        goToPage(page){
            this.paginationModel.currentPage=page;
            this.refresh();
        },
        previous(){
            this.paginationModel.currentPage--;
            this.refresh();
        },
        next(){
            this.paginationModel.currentPage++;
            this.refresh();
        },
        setPages(){
            this.paginationModel.pages=[1];
            var min = 2;
            var max = this.paginationModel.maxPages-1;
            if (max > 6){
                max = 5;
                if (this.paginationModel.currentPage>this.paginationModel.maxPages-4)
                    max = this.paginationModel.maxPages-1
                else if (this.paginationModel.currentPage>4)
                    max = this.paginationModel.currentPage+1;
                if (this.paginationModel.currentPage<5)
                    min=2;
                else
                    min = Math.min(this.paginationModel.currentPage-1, this.paginationModel.maxPages-4);
            }
            if (min > 3)
                this.paginationModel.pages.push('..');
            for (var x = min;x <= max;x++){
                this.paginationModel.pages.push(x);
            }
            if (max < this.paginationModel.maxPages-1)
                this.paginationModel.pages.push('..');
            if (this.paginationModel.maxPages > 1)
                this.paginationModel.pages.push(this.paginationModel.maxPages);
        }
    },
    template:   `<alert-component :model=alertModel></alert-component>
                <div>
                    <loading-button-component class="btn-primary btn-sm" @click="refresh" :exloading=isloading>
                        <template #defaultLabel>
                            <i class="fa fa-sync-alt"></i>
                        </template>
                    </loading-button-component>
                    <v-paging :model=paginationModel @previous=previous @next=next @goToPage=goToPage></v-paging>
                </div>
                <spinner-component v-if="isloading"></spinner-component>
                <v-table v-if="!isloading" :columns="columns" :rows=rows>
                    <template v-slot:default="row">
                        <slot v-bind="row"/>
                    </template>
                </v-table>`
}