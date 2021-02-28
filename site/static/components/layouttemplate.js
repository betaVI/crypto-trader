export default{
    name:"Layout",
    template:   `<div>
                    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                        <ul class="navbar-nav mr-auto">
                            <li><router-link class="navbar-brand" href="/">Dashboard</router-link></li>
                            <li><router-link class="nav-link" href="/test">Test</router-link></li>
                        </ul>
                    </nav>
                    <div class="container-fluid">
                        <slot></slot>
                    </div>
                </div>`
}