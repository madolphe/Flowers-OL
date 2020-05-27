class MOT{
    constructor(n_targets, n_distractors, area_max, area_min, radius, speed_min, speed_max)
    {
        this.area_max = area_max;
        this.area_min = area_min;
        this.n_targets = n_targets;
        this.n_distractors = n_distractors;
        this.targets = [];
        this.distractors = [];
        this.frozen = false;
        this.hover = false;
        this.phase = 'init';
        this.speed_min = speed_min;
        this.speed_max = speed_max;
        this.radius = radius;
        this.init_lists();
        this.all_objects = this.targets.concat(this.distractors);
    }
    init_lists(){
        // to be overwritten if non primitive objects are used
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Tracked_Object(this.speed_min, this.speed_max, step, this.area_min, this.area_max,
                'target', this.targets, this.radius))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.distractors.push(new Tracked_Object(this.speed_min, this.speed_max,step+this.n_targets,
                this.area_min, this.area_max, 'distractor', this.targets.concat(this.distractors), this.radius));
        }
    }

    freeze_app(){
        this.frozen = !this.frozen;
    }
    move_objects(){
        // function used to display all balls
        if (!this.frozen){
            this.all_objects.forEach(function (item){item.move()});
        }
    }
    details(){
        console.log(this.frozen)
    }
    change_to_same_color(){
        this.all_objects.forEach(function (item){item.color = 'white'});
    }
    change_target_color(){
        // if(this.phase=='got_response'){this.unselect_objects()} //all objects are getting unselected}
        this.targets.forEach(function(item){
            item.color = 'green';
        });
        // this.distractors.forEach(function(item){item.color = 'yellow'});
    }
    display_objects(mouseX, mouseY){
        // function used to display all balls
        this.all_objects.forEach(function (item){item.display(mouseX, mouseY)});
    }
    enable_interact(){
        this.all_objects.forEach(function (item){item.interact_phase = true});
    }
    check_collisions(){
        for(let i =0; i< this.all_objects.length; i++){
            for (let j=0 ; j< this.all_objects.length; j++){
                if(j!=i){
                    this.all_objects[i].contact(this.all_objects[j]);
                }
            }
        }
    }
    check_mouse_pressed(mouseX, mouseY){
        //if(app.phase != 'got_response'){this.all_objects.forEach(function (item){item.is_pressed(mouseX, mouseY)})}
        this.all_objects.forEach(function (item){item.is_pressed(mouseX, mouseY)})
    }
    unselect_objects(){
        // this.all_objects.forEach(function (item){item.pressed = false});
        this.all_objects.forEach(function(item){item.pres = true;})
    }
    get_results(){
        let nb_target_retrieved = 0;
        let nb_distract_retrieved = 0;
        this.targets.forEach(function (item) {if(item.pressed){nb_target_retrieved ++}});
        this.distractors.forEach(function (item) {if(!item.pressed){nb_distract_retrieved ++}});
        return [nb_target_retrieved, nb_distract_retrieved]
    }
}
