export default{
    name:"Pagination",
    props:["model"],
    emits:["previous","goToPage","next"],
    template:   `<nav class="float-right">
                    <ul class="pagination pagination-sm">
                        <li class="page-item" :class="{ disabled: model.currentPage == 1 }">
                            <a class="page-link" @click="$emit('previous')">
                                <i class="fa fa-step-backward"></i>
                            </a>
                        </li>
                        <li v-for="page in model.pages" class="page-item" :class="{ active: model.currentPage == page, disabled: model.page=='..' }" :style="{ cursor: model.page == '..' ? 'not-allowed': 'default' }">
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
                </nav>`
}