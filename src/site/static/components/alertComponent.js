export default{
    name: 'AlertComponent',
    props: ['model'],
    emits: ['dismissed'],
    methods:{
        alertDismissed(){
            this.model.display=false;
            this.$emit('dismissed');
        }
    },
    template:   `<div class="alert" :class="model.success ? 'alert-success' : 'alert-danger'" v-if="model.display">
                    <span>{{ model.message }}</span>
                    <button type="button" class="close" aria-label="Close" @click.prevent=alertDismissed>
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>`
}