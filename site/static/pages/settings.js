export default{
    name: "Settings",
    data(){
        return {
            alertmodel:{
                display:false,
                success:false,
                message:''
            },
            interval: 5,
            loglevel: 10,
            levels:[]
        }
    },
    mounted(){
        this.loadForm();
    },
    methods:{
        async loadForm(){
            try{
                const response = await fetch('/api/settings', { method: "GET" });
                const data = await response.json();
                if (data.success){
                    this.levels = data.loglevels;
                    this.interval = data.interval;
                    this.loglevel = data.loglevel;
                }
                else
                    this.displayAlert(data.success, data.message);
            } 
            catch(error){
                this.displayAlert(false, 'Failed to load form: ' + error);
            }
        },
        async postForm(){
            try{
                var body = JSON.stringify({ interval: this.interval, loglevel: this.loglevel });
                const response = await fetch('/api/settings', {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: body
                });
                const data = await response.json();
                this.displayAlert(data.success,data.message);
            }
            catch(error){
                this.displayAlert(false, 'Failed to post form: ' + error);
            }
        },
        displayAlert(success, message){
            this.alertmodel.display=true;
            this.alertmodel.success = success;
            this.alertmodel.message = message;
        }
    },
    template:   `<layout>
                    <alert-component :model="alertmodel"></alert-component>
                    <h3>Settings</h3>
                    <div class="form-group row col-3">
                        <label>Check Interval (in seconds):</label>
                        <input class="form-control" v-model="interval" />
                    </div>
                    <div class="form-group row col-3">
                        <label>Log Level:</label>
                        <select class="form-control" v-model="loglevel">
                            <option v-for="level in levels" :value="level[0]">{{ level[1] }}</option>
                        </select>
                    </div>
                    <button class="btn btn-success" @click="postForm">Save</button>
                </layout>`
}