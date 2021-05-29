import routes from './routes.js'

export default{
    data: () =>({
        currentRoute: window.location.pathname
    }),
    computed:{
        ViewComponent(){
            // console.log(this.currentRoute)
            const matchingPage = routes[this.currentRoute]
            return matchingPage;
        }
    },
    render(){
        return Vue.h(this.ViewComponent);
    },
    created(){
        window.addEventListener('popstate', ()=>{
            this.currentRoute = window.location.pathname;
        })
    }
}