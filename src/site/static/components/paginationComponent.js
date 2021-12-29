export default{
    name:"Pagination",
    props:["model"],
    emits:["previous","goToPage","next", "setPageSize"],
    template:   `<div :class="$attrs.class">
                    <div class="dropdown float-left">
                        <a class="btn btn-sm dropdown-toggle" type="button" data-toggle="dropdown">
                            {{ model.pagesize }}
                        </a>
                        <div class="dropdown-menu">
                            <a class="dropdown-item" style="width:auto;" @click="$emit('setPageSize', 20)">20</a>
                            <a class="dropdown-item" style="width:auto;" @click="$emit('setPageSize', 50)">50</a>
                            <a class="dropdown-item" style="width:auto;" @click="$emit('setPageSize', 100)">100</a>
                            <a class="dropdown-item" style="width:auto;" @click="$emit('setPageSize', 200)">200</a>
                        </div>
                    </div>
                    <nav class="float-right">
                        <ul class="pagination pagination-sm">
                            <li class="page-item" :class="{ disabled: model.currentPage == 1 }">
                                <a class="page-link" @click="$emit('previous')">
                                    <i class="fa fa-step-backward"></i>
                                </a>
                            </li>
                            <li v-for="page in model.pages" class="page-item" :class="{ active: model.currentPage == page, disabled: page=='..'?true:false }" :style="{ cursor: page == '..' ? 'not-allowed': 'default' }">
                                <a class="page-link" @click="$emit('goToPage',page)">
                                    {{ page }}
                                </a>
                            </li>
                            <li class="page-item" :class="{ disabled: model.currentPage == model.maxPages }">
                                <a class="page-link" @click="$emit('next')">
                                    <i class="fa fa-step-forward"></i>
                                </a>
                            </li>
                        </ul>
                    </nav>
                </div>`
}