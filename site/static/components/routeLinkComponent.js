import routes from '../navigation/routes.js'

export default{
    name: 'RouteLink',
    props:{
        href:{
            type:String,
            required: true
        }
    },
    methods:{
        go(){
            this.$root.currentRoute = this.href;
            window.history.pushState(null, routes[this.href], this.href);
        }
    },
    template:   `<a :href=href :class="$attrs.class" @click.prevent="go">
                    <slot></slot>
                </a>`
}