export default{
    name:"Table Component",
    props:["columns", "rows"],
    template:   `<div class="text-center border" v-if="rows.length == 0"><span>No Data to display</span></div>
                <table v-if="rows.length > 0" class="table table-bordered table-sm">
                    <thead>
                        <tr>
                            <th v-for="column in columns" :class=column.class>{{ column.name }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <slot v-for="( row, index ) in rows" :item="row"></slot>
                    </tbody>
                </table>`
}