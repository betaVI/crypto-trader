export default{
    name: "LoadingButtonComponent",
    props: ['exloading'],
    watch:{
        exloading: function(exloading){
            this.isloading=exloading;
        }
    },
    data(){
        return {
            isloading:false
        };
    },
    methods:{
        buttonClicked(){
            this.isloading = true;
        }
    },
    template:   `<button type="button" class="btn" :class="$attrs.class" :disabled=isloading @click=buttonClicked>
                    <slot name="defaultLabel" v-if="!isloading"></slot>
                    <slot name="loadingLabel" v-if="isloading">
                        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    </slot>
                </button>`
}