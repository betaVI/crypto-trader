export default{
    name:"Table Component",
    props:["columns", "rows"],
    template:   `<table id="logs" class="table table-bordered table-sm">
                    <thead>
                        <tr>
                            <th v-for="column in columns">{{ column }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <slot v-for="( row, index ) in rows" :item="row"></slot>
                    </tbody>
                </table>`
}