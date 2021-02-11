export default{
    name: 'SpinnerComponent',
    props: ['isloading'],
    template: `<div class="d-flex justify-content-center" v-if="isloading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="sr-only">Loading...</span>
                    </div>
                </div>`
}