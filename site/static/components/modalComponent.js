export default{
    name: "ModalComponent",
    props: [ 'model', 'alertmodel'],
    emits: [ 'accepted', 'alertDismissed' ],
    template:   `<div class="modal fade" tabindex="-1" role="dialog" data-backdrop="static">
                    <div class="modal-dialog modal-lg" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <slot name="header"></slot>
                            </div>
                            <div class="modal-body">
                                <alert-component :model=alertmodel @dismissed="$emit('alertDismissed')"></alert-component>
                                <spinner-component v-if=model.isloading></spinner-component>
                                <slot name="body"></slot>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-danger mr-auto" data-dismiss="modal" :disabled="model.issubmitting">
                                    Cancel
                                </button>
                                <button id="submit" type="button" class="btn btn-primary" @click="$emit('accepted')" v-if="!model.issubmitting">
                                    <slot name="btnSubmit">Submit</slot>
                                </button>
                                <button type="button" class="btn btn-primary" disabled v-if="model.issubmitting">
                                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                    Loading...
                                </button>
                            </div>
                        </div>
                    </div>
                </div>`
}