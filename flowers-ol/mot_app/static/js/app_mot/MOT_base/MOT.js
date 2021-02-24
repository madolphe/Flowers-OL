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
        this.positions = this.discrete_space();
        this.init_lists();
        this.all_objects = this.targets.concat(this.distractors);
    }
    // INIT FUNCTIONS //
    discrete_space(){
        let complete = false;
        let r = this.area_min + this.radius;
        let positions = [];
        // Make sure radius is not too big for space in scene:
        if(this.radius>(this.area_max-this.area_min)){
            alert("Radius is too large, we automaticaly set it to 45 (default value)");
            this.radius = 45;
            this.discrete_space();
        }
        // Discretize space:
        while(!complete){
            // first compute current circle perimeter:
            // var perimeter = 2*Math.PI*r;
            // var nb_pos = perimeter / 2*this.radius;
            // Get number of position on this circle:
            var nb_pos = Math.floor(Math.PI*r/(2*this.radius));
            // Get angle step:
            var step = Math.floor(360/nb_pos);
            for(let i= 0; i<nb_pos; i++){
                positions.push([i*step, r])
            }
            // update r and check that it still fits in scene:
            if(r<this.area_max-3*this.radius){
                r=r+2*this.radius;
            }else{
                complete = true;
            }
        }
        // Depending on radius, number of available positions decrease
        // Make sure to display only max number of elements (otherwise init_lists is an infinite loop)
        let has_removed = false;
        while(positions.length<this.n_targets+this.n_distractors){
            has_removed = true;
            if(this.n_distractors > 0){
                this.n_distractors --;
            }else{
                this.n_targets --;
            }
        }
        if(has_removed){alert("Too many objects, we automaticaly remove those that didn't fit!");}
        return positions;
    }
    init_lists(){
        // This is overwritten if non primitive objects are used
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Tracked_Object(this.speed_min, this.speed_max, step, this.area_min, this.area_max,
                'target', this.targets, this.radius, this.positions))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.distractors.push(new Tracked_Object(this.speed_min, this.speed_max,step+this.n_targets,
                this.area_min, this.area_max, 'distractor', this.targets.concat(this.distractors), this.radius,
                this.positions));
        }
    }

    // PLAY LOOP, DO 3 ACTIONS : //
    // 1_ DISPLAY (LAST POSITION) //
    display_objects(mouseX, mouseY){
        // function used to display all balls
        this.all_objects.forEach(function (item){item.display(mouseX, mouseY)});
    }
    // 2_ CHECK COLLISIONS //
    // THEN CHECK COLLISIONS IF OBJECTS FOLLOWS THE DIRECTION //
    check_collisions(){
        // First update speed to compare next moves:
        this.random_deviation();
        for(let i=0; i< this.all_objects.length; i++){
            for (let j=0 ; j< this.all_objects.length; j++){
                    if(j!=i){
                        this.all_objects[i].contact(this.all_objects[j]);
                    }
                }
            }
        this.reflection_tests();
    }
    random_deviation(){
        this.all_objects.forEach(function (item) {
            item.speed_random_variation();
        })
    }
    reflection_tests(){
        this.all_objects.forEach(function (item) {
            item.check_limits();
        })
    }

    // 3_ MOVE TO NEW POS //
    move_objects(){
        // function used to display all balls
        if (!this.frozen){
            this.all_objects.forEach(function (item){item.move()});
        }
    }

    // APP PHASES + ADD VISUALS //
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
    enable_interact(){
        this.all_objects.forEach(function (item){item.interact_phase = true});
    }
    check_mouse_pressed(mouseX, mouseY){
        //if(app.phase != 'got_response'){this.all_objects.forEach(function (item){item.is_pressed(mouseX, mouseY)})}
        this.all_objects.forEach(function (item){item.is_pressed(mouseX, mouseY)})
    }
    unselect_objects(){
        // this.all_objects.forEach(function (item){item.pressed = false});
        this.all_objects.forEach(function(item){item.pres = true;})
    }
    freeze_app(){
        this.frozen = !this.frozen;
    }
    get_results(){
        let nb_target_retrieved = 0;
        let nb_distract_retrieved = 0;
        this.targets.forEach(function (item) {if(item.pressed){nb_target_retrieved ++}});
        this.distractors.forEach(function (item) {if(!item.pressed){nb_distract_retrieved ++}});
        return [nb_target_retrieved, nb_distract_retrieved]
    }
}
