class MOT_Game_Light extends MOT{
    constructor(n_targets, n_distractors, area_max, area_min, radius, speed_min, speed_max, target_color, distract_color,
                positions){
        super(n_targets, n_distractors, area_max, area_min, radius, speed_min, speed_max, positions);
        this.target_color = target_color;
        this.distract_color = distract_color;
        this.targets = [];
        this.distractors = [];
        this.init_lists();
        this.all_objects = this.targets.concat(this.distractors);
    }
    init_lists() {
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Tracked_Object_Game_Light(this.speed_min, this.speed_max, step, this.area_min, this.area_max,
                'target', this.targets, this.radius, this.target_color, this.distract_color))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.distractors.push(new Tracked_Object_Game_Light(this.speed_min, this.speed_max,step+this.n_targets,
                this.area_min, this.area_max, 'distractor', this.targets.concat(this.distractors), this.radius,
                this.target_color, this.distract_color));
        }
    }
    freeze_app() {
        super.freeze_app();
    }
    discrete_space() {
        return super.discrete_space();
    }
    display_objects(mouseX, mouseY) {
        push();
        ellipseMode(CENTER);
        stroke('white');
        noFill();
        strokeWeight(4);
        ellipse(windowWidth/2, windowHeight/2, Math.round(ppd*max_angle));
        pop();
        push();
        ellipseMode(CENTER);
        stroke('white');
        noFill();
        strokeWeight(2);
        ellipse(windowWidth/2, windowHeight/2, Math.round(ppd*min_angle));
        pop();
        super.display_objects(mouseX, mouseY);
    }
    check_collisions() {
        super.check_collisions();
    }
    move_objects() {
        super.move_objects();
    }
    change_target_color() {
        //super.change_target_color();
        this.targets.forEach(function(item){
            item.actual_color = item.target_color;
        });
        this.distractors.forEach(function(item){
            item.actual_color = item.distract_color;
        })
    }
    change_to_same_color() {
        //super.change_to_same_color();
        this.all_objects.forEach(function(item){
            item.actual_color = item.distract_color;
        })
    }
    enable_interact() {
        super.enable_interact();
    }
    check_mouse_pressed(mouseX, mouseY) {
        super.check_mouse_pressed(mouseX, mouseY);
    }
    unselect_objects() {
        super.unselect_objects();
    }
    get_results() {
        return super.get_results();
    }
}