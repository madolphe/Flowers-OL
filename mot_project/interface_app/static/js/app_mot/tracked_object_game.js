class Tracked_Object_Game extends Tracked_Object{
    constructor(speed_min, speed_max, name, area_min, area_max, type, forbidden_loc, radius, target_image, distract_image){
        super(speed_min, speed_max, name, area_min, area_max, type, forbidden_loc, radius);
        this.target_image = target_image;
        this.distract_image = distract_image;
        this.actual_image = this.distract_image;
    }
    initial_position(forbidden_loc) {
        super.initial_position(forbidden_loc);
    }
    update_next_boundaries() {
        super.update_next_boundaries();
    }
    check_collision(object) {
        return super.check_collision(object);
    }
    check_initial_contact(object) {
        return super.check_initial_contact(object);
    }
    contact(object) {
        super.contact(object);
    }
    add_hover() {
        super.add_hover();
    }
    display_speed() {
        super.display_speed();
    }
    display(X, Y) {
        // super.display(X,Y);
        this.event_display(X, Y);
        push();
        translate(this.pos.x+windowWidth/2, this.pos.y+windowHeight/2);
        imageMode(CENTER);
        scale(0.5);
        image(this.actual_image, 0, 0);
        pop();
    }
    event_display(X, Y) {
        if(this.interact_phase){
            if(this.pressed){
                this.color = 'green';
                push();
                strokeWeight(2);
                stroke(this.color);
                noFill();
                ellipse(this.pos.x+ windowWidth/2, this.pos.y+windowHeight/2, this.radius);
                pop();
            }
            else{
                if(abs((this.pos.x+windowWidth/2)-X)<this.radius/2 && abs((this.pos.y+windowHeight/2)-Y)<this.radius/2)
                {
                this.color = 'white';
                push();
                strokeWeight(2);
                stroke(this.color);
                noFill();
                ellipse(this.pos.x+ windowWidth/2, this.pos.y+windowHeight/2, this.radius);
                pop();
                }
            }
        }
    }
    change_pos() {
        super.change_pos();
    }
    move() {
        super.move();
    }
    reflect_speed() {
        super.reflect_speed();
    }
    is_pressed(X, Y) {
        super.is_pressed(X, Y);
    }
    drawArrow(base, vec, myColor) {
        super.drawArrow(base, vec, myColor);
    }
}