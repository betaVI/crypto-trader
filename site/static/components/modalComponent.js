export default{
    name: "ModalComponent",
    props: [ 'modalcontentloading', 'issubmitting', 'alertsuccess', 'alertmessage', 'showalert'],
    emits: [ 'accepted' ],
    methods:{
        alertDismissed(){
            this.props.showalert=false;
        }
    },
    template:   `<div class="modal fade" tabindex="-1" role="dialog" data-backdrop="static">
                    <div class="modal-dialog modal-lg" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <slot name="header"></slot>
                            </div>
                            <div class="modal-body">
                                <div class="alert" :class="alertsuccess ? 'alert-success' : 'alert-danger'" v-if="showalert">
                                    <span>{{ alertmessage }}</span>
                                    <button type="button" class="close" data-dismiss="alert" aria-label="Close" @click="alertDismissed">
                                        <span aria-hidden="true">&times;</span>
                                    </button>
                                </div>
                                <div class="d-flex justify-content-center" v-if="modalcontentloading">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="sr-only">Loading...</span>
                                    </div>
                                </div>
                                <slot name="body"></slot>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-danger mr-auto" data-dismiss="modal" :disabled="issubmitting">
                                    Cancel
                                </button>
                                <button id="submit" type="button" class="btn btn-primary" @click="$emit('accepted', $event)" v-if="!issubmitting">
                                    <slot name="btnSubmit">Submit</slot>
                                </button>
                                <button type="button" class="btn btn-primary" disabled v-if="issubmitting">
                                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                    Loading...
                                </button>
                            </div>
                        </div>
                    </div>
                </div>`
}