export default{
    name:"Layout",
    template:   `<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                    <ul class="navbar-nav mr-auto">
                        <li><router-link class="navbar-brand" href="/">Dashboard</router-link></li>
                        <li><router-link class="nav-link" href="/diagnostics">Diagnostics</router-link></li>
                        <li><router-link class="nav-link" href="/settings">Settings</router-link></li>
                    </ul>
                </nav>
                <div class="container-fluid">
                    <slot></slot>
                </div>`
}