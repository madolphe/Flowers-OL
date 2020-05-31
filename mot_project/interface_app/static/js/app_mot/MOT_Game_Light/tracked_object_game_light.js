class Tracked_Object_Game_Light extends Tracked_Object{
    constructor(speed_min, speed_max, name, area_min, area_max, type, forbidden_loc, radius, target_color, distract_color){
        super(speed_min, speed_max, name, area_min, area_max, type, forbidden_loc, radius);
        this.target_color = target_color;
        this.distract_color = distract_color;
        this.actual_color = this.distract_color;
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
        fill(this.actual_color);
        ellipse(0, 0, this.radius);
        pop();
    }
    event_display(X, Y) {
        if(this.interact_phase){
            if(this.pressed){
                push();
                strokeWeight(2);
                stroke('white');
                noFill();
                ellipse(this.pos.x+ windowWidth/2, this.pos.y+windowHeight/2, 1.1*this.radius);
                pop();
            }
            else{
                if(abs((this.pos.x+windowWidth/2)-X)<this.radius/2 && abs((this.pos.y+windowHeight/2)-Y)<this.radius/2)
                {
                push();
                strokeWeight(2);
                stroke('white');
                noFill();
                ellipse(this.pos.x+ windowWidth/2, this.pos.y+windowHeight/2, 1.1*this.radius);
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