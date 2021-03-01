class MOT_Game extends MOT{
    constructor(n_targets, n_distractors, area_max, area_min, radius, speed_min, speed_max, target_image, distract_image){
        super(n_targets, n_distractors, area_max, area_min, radius, speed_min, speed_max);
        this.target_image = target_image;
        this.distract_image = distract_image;
        this.targets = [];
        this.distractors = [];
        this.init_lists();
        this.all_objects = this.targets.concat(this.distractors);
    }
    init_lists() {
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Tracked_Object_Game(this.speed_min, this.speed_max, step, this.area_min, this.area_max,
                'target', this.targets, this.radius, this.target_image, this.distract_image, this.positions))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.distractors.push(new Tracked_Object_Game(this.speed_min, this.speed_max,step+this.n_targets,
                this.area_min, this.area_max, 'distractor', this.targets.concat(this.distractors), this.radius,
                this.target_image, this.distract_image, this.positions));
        }
    }
    discrete_space() {
        return super.discrete_space();
    }

    freeze_app() {
        super.freeze_app();
    }

    display_objects(mouseX, mouseY) {
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
            item.actual_image = item.target_image;
        });
        this.distractors.forEach(function(item){
            item.actual_image = item.distract_image;
        })
    }
    change_to_same_color() {
        //super.change_to_same_color();
        this.all_objects.forEach(function(item){
            item.actual_image = item.distract_image;
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