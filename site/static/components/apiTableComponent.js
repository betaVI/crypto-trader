export default{
    name: "API Table",
    props: ['endpoint', 'columns', 'filtertitle'],
    emits: ['dataloaded'],
    data(){
        return {
            rows:[],
            isloading:false,
            currentSort:'createdat',
            currentSortDir: 'desc',
            paginationModel:{
                pages:[],
                currentPage:1,
                pagesize:20,
                maxPages:1
            },
            filtermodel:{
                title:"",
                content:"",
                issubmitting:false,
                isloading:false,
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
                if (this.hasFilters()){
                    var filters=[];
                    this.columns.forEach(c=>{
                        if (c.filter && c.filter.value){
                            filters.push({
                                name: c.name,
                                value: c.filter.value,
                                operator: '='
                            })
                        }
                    });
                }
                var body = JSON.stringify({filters:filters});
                const result = await fetch(this.endpoint+this.paginationModel.pagesize+'/'+this.paginationModel.currentPage+'/'+this.currentSort+'/'+this.currentSortDir, { 
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: body
                });
                const data = await result.json();
                if (data.success){
                    this.paginationModel.maxPages = Math.ceil(data.totalcount/this.paginationModel.pagesize);
                    this.rows = data.data;
                    this.$emit('dataloaded',data);
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
        },
        hasFilters(){
            var filter = this.columns.find(c=>c.filter!=null)
            return filter!=null;
        },
        openFilters(){
            this.filtermodel.title = this.filtertitle;
            $(this.$refs.filters.$el).modal('show');
        },
        applyFilters(){
            this.currentPage=1;
            this.refresh();
            $(this.$refs.filters.$el).modal('hide');
        }
    },
    template:   `<alert-component :model=alertModel></alert-component>
                <div>
                    <loading-button-component class="btn-primary btn-sm" @click="refresh" :exloading=isloading>
                        <template #defaultLabel>
                            <i class="fa fa-sync-alt"></i>
                        </template>
                    </loading-button-component>
                    <button v-if="hasFilters()" class="btn btn-secondary btn-sm" @click=openFilters>
                        <i class="fa fa-filter"></i>
                    </button>
                    <v-paging class="float-right" :model=paginationModel @previous=previous @next=next @goToPage=goToPage></v-paging>
                </div>
                <spinner-component v-if="isloading"></spinner-component>
                <modal ref="filters" @accepted=applyFilters :model=filtermodel>
                    <template v-slot:header>
                        <h5 class="modal-title">{{ filtermodel.title }}</h5>
                    </template>
                    <template v-slot:body>
                        <template v-for="column in columns">
                            <div class="form-group row" v-if="column.filter != null">
                                <label class="col-lg-2 col-md-2 col-sm-2" v-if="column.filter != null">{{ column.name }}:</label>
                                <div v-if="column.type == Date" class="btn-group btn-group-sm btn-group-toggle">
                                    <label class="btn btn-outline-primary" :class="{ active: column.filter.value == ''}">
                                        <input type="radio" value="" v-model="column.filter.value"/>
                                        All
                                    </label>
                                    <label class="btn btn-outline-primary" :class="{ active: column.filter.value == '1m'}">
                                        <input type="radio" value="1m" v-model="column.filter.value"/>
                                        1 m
                                    </label>
                                    <label class="btn btn-outline-primary" :class="{ active: column.filter.value == '15m'}">
                                        <input type="radio" value="15m" v-model="column.filter.value"/>
                                        15 m
                                    </label>
                                    <label class="btn btn-outline-primary" :class="{ active: column.filter.value == '1h'}">
                                        <input type="radio" value="1h" v-model="column.filter.value"/>
                                        1 h
                                    </label>
                                    <label class="btn btn-outline-primary" :class="{ active: column.filter.value == '6h'}">
                                        <input type="radio" value="6h" v-model="column.filter.value"/>
                                        6 h
                                    </label>
                                    <label class="btn btn-outline-primary" :class="{ active: column.filter.value == '1d'}">
                                        <input type="radio" value="1d" v-model="column.filter.value"/>
                                        1 d
                                    </label>
                                    <label class="btn btn-outline-primary" :class="{ active: column.filter.value == '1w'}">
                                        <input type="radio" value="1w" v-model="column.filter.value"/>
                                        1 w
                                    </label>
                                </div>
                                <select class="col-lg-6 col-md-4 col-sm-2 form-control" v-if="column.filter.type == 'dropdown'" v-model="column.filter.value">
                                    <option v-for="choice in column.filter.choices" :value="choice.value">{{ choice.text }}</option>
                                </select>
                            </div>
                        </template>
                    </template>
                </modal>
                <v-table v-if="!isloading" :columns=columns :rows=rows>
                    <template v-slot:default="row">
                        <slot v-bind="row"/>
                    </template>
                </v-table>`
}