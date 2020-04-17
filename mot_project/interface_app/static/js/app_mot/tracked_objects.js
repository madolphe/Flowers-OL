// @ TODO : recode speed init!

class Tracked_Object{
    constructor(speed_min, speed_max, name, area_min, area_max, type, forbidden_loc, radius){
        this.radius = radius; // in pixels
        // initial speed
        this.speedx = Math.round(Math.random()) > 0 ? random(speed_min, speed_max) : random(-speed_min, -speed_max);
        this.speedy = Math.round(Math.random()) > 0 ? random(speed_min, speed_max) : random(-speed_min, -speed_max);
        // Create a velocity vector
        this.speed = createVector(this.speedx, this.speedy);
        this.base_vect = createVector(1,0);
        this.angle_speed = this.base_vect.angleBetween(this.speed);
        this.norm_speed = norm(this.speed);

        //this.angle_speed = Math.sign(this.y>0) ?
        //    Math.round((Math.acos(this.speedx/Math.sqrt(this.speedx**2+this.speedy**2)))) :
        //    Math.PI*2 - Math.round((Math.acos(this.speedx/Math.sqrt(this.speedx**2+this.speedy**2))));

        // Boundaries:
        this.area_min = area_min; // in pixels
        this.area_max = area_max; // in pixels

        // We don't want our objects to overlap when initializing :
        this.initial_position(forbidden_loc);

        this.name = name;
        this.hover = false;
        this.pressed = false;
        this.answer = false;
        this.type = type;
        this.pos_next = createVector(0,0);
        this.impact = [[this.x, this.y]];
        sessionStorage.setItem(this.name, 0);
    }

    initial_position(forbidden_loc){
        let i = 0;
        this.r = random(this.area_min + this.radius, this.area_max - this.radius);
        this.theta = random(0,2*Math.PI);
        this.x = Math.round(this.r*Math.cos(this.theta));
        this.y = Math.round(this.r*Math.sin(this.theta));
        let number = 0;
        while (i<forbidden_loc.length) {
            if(!this.check_initial_contact(forbidden_loc[i])){
                // ok object does'nt collide with i-th, look at next one:
                i=i+1;
            }
            else{
                // object are overlapping, start again:
                number++;
                i=0;
                this.r = random(this.area_min + this.radius, this.area_max - this.radius);
                this.theta = random(0,2*Math.PI);
                this.x = Math.round(this.r*Math.cos(this.theta));
                this.y = Math.round(this.r*Math.sin(this.theta));
            }
        }
        // Note: this.x and this.y will save initial pos
        // this.pos is the moving location of object
        this.pos = createVector(this.x, this.y)
    }

    update_next_boundaries(){
        this.pos_next.x = this.pos.x + this.speed.x;
        this.pos_next.y = this.pos.y + this.speed.y;
    }

    check_initial_contact(object){
        // returns true if object is in contact with an other one
        return (Math.sqrt((this.x - object.pos.x)**2 + (this.y - object.pos.y)**2) < this.radius)
    }

    check_collision(object){
        // returns true if object is in contact with an other one
        return (Math.sqrt((this.pos_next.x - object.pos.x)**2 + (this.pos_next.y - object.pos.y)**2) < this.radius)
    }

    contact(object){
        this.update_next_boundaries();
        // object.update_next_boundaries();
        if(this.check_collision(object)){
            let sx =  object.speed.x;
            let sy =  object.speed.y;
            object.speed.x = this.speed.x;
            object.speed.y = this.speed.y;
            this.speed.x = sx;
            this.speed.y = sy;
        }
    }

    add_hover(){
        push();
        translate(this.x, this.y);
        fill('red');
        ellipse(0, 0, this.radius, this.radius);
        pop();
    }

    display(X, Y){
        this.event_display(X, Y);
        push();
        strokeWeight(2);
        if(this.type=='target'){
            stroke('green');
        }else{
            stroke('red')
        }
        noFill();
        // Poisition isn't translated to the center of the canvas, we do it when displaying:
        line(this.pos.x - this.radius/2 + windowWidth/2,
            this.pos.y+windowHeight/2,
            this.pos.x+this.radius/2+ windowWidth/2,
            this.pos.y+windowHeight/2);
        line(this.pos.x + windowWidth/2,
            this.pos.y - this.radius/2 + windowHeight/2,
            this.pos.x+ windowWidth/2,
            this.pos.y + this.radius/2 + windowHeight/2);
        ellipse(this.pos.x+ windowWidth/2, this.pos.y+windowHeight/2, this.radius);
        pop();
        push();
        fill('white');
        rectMode(CENTER);
        textSize(12);
        text(this.name, this.pos.x+ 12+windowWidth/2, this.pos.y+12+windowHeight/2);
        pop();
        this.display_speed();
    }

    display_speed(){
        // theta between 0 and 2PI
        push();
        stroke('white');
        strokeWeight(3);
        pop();
        push();
        textSize(11);
        fill('white');
        text('ang speed:   '+(degrees(this.angle_speed).toFixed(2)).toString(),
            this.pos.x-22+windowWidth/2, this.pos.y-55+windowHeight/2);

        text('R:   '+Math.round(this.r).toString(),
            this.pos.x-22+windowWidth/2, this.pos.y-45+windowHeight/2);

        text('Theta:   '+(degrees(this.pos.heading()).toFixed(2)).toString(),
            this.pos.x-22+windowWidth/2, this.pos.y-35+windowHeight/2);

        text('Speedx:  '+this.speed.x.toFixed(2).toString(),
            this.pos.x-22+windowWidth/2, this.pos.y-25+windowHeight/2);

        text('Speedy:  '+this.speed.y.toFixed(2).toString(),
            this.pos.x-22+windowWidth/2, this.pos.y-15+windowHeight/2);
        pop();
        push();
        strokeWeight(5);
        angleMode(DEGREES);
        translate(this.pos.x+windowWidth/2, this.pos.y+windowHeight/2);
        rotate(degrees(this.angle_speed));
        // line(0, 0, 10*this.speedx, 10*this.speedy);
        pop();
        // display theta direction:
        push();
        strokeWeight(5);
        stroke('white');
        translate(this.pos.x+windowWidth/2, this.pos.y+windowHeight/2);
        angleMode(DEGREES);
        rotate(degrees(this.theta));
        // line(0, 0, 40, 0);
        pop();
        pop();
        if(this.impact.length>2){
            let i = 0;
            while(i<this.impact.length-1){
                fill('red');
                ellipse(this.impact[i][0]+windowWidth/2, this.impact[i][1]+windowHeight/2, 10);
                stroke('white');
                //line(this.impact[i][0]+windowWidth/2, this.impact[i][1]+windowHeight/2,
                //    this.impact[i+1][0]+windowWidth/2, this.impact[i+1][1]+windowHeight/2);
                i++;
                }
            }
        push();
    }

    event_display(X, Y){
        if(this.hover){
            if(this.pressed){
                if(!this.answer){
                    // Not the time to reveal yet:
                    // this.color = 'green';
                    this.add_hover();
                }else{
                    // Time to show answer!
                    if(this.type == 'target'){
                        // user has clicked, well done
                        this.add_hover();
                    }else{
                        // user should have clicked but missed
                        // this.add_hover();
                    }
                }
            }
            else{
                if(!this.answer){
                    // If this is not reveal time:
                    this.color = 'white';
                    if(abs(this.x-X)<this.image_width && abs(this.y-Y)<this.image_height) {
                        this.add_hover();
                    }
                }else{
                    // Time to show answer:
                    if(this.type=='target'){
                        // user should have clicked on this one but missed it:
                        this.color = 'white';
                        //this.add_hover();
                    }else{
                        this.color = 'white';
                    }
                }
            }
        }
    }

    change_pos(){
        // this.x = Math.round(this.x+this.speedx);
        // this.y = Math.round(this.y+this.speedy);
        // this.r = Math.sqrt(this.x**2 + this.y**2);
        //this.pos.x = Math.round(this.pos.x+this.speed.x);
        //this.pos.y = Math.round(this.pos.y+this.speed.y);
        //this.pos.set(Math.round(this.pos.x+this.speed.x), Math.round(this.pos.y+this.speed.y));
        this.pos.add(this.speed);
        //this.theta = this.base_vect.angleBetween(this.pos);
        this.theta = this.pos.heading();

        //this.theta = ( Math.sign(this.y) > 0)?
        //    Math.acos(this.x/this.r) :
        //    Math.PI*2 - (Math.acos(this.x/this.r));

        // this.norm_speed = Math.sqrt(this.speedx**2+this.speedy**2);
        // this.norm_speed = norm(this.speed);

        //this.angle_speed = (Math.sign(this.speedy) >0) ?
        //     Math.acos(this.speedx/this.norm_speed) :
        //     Math.PI*2 - Math.acos(this.speedx/this.norm_speed);
        // this.angle_speed = angleBetween(this.base_vect, this.speed)
    }

    move(){
        // Function to change direction (constraints on motion)
        // if(this.r + this.radius> this.area_max){
        if(this.pos.mag() + this.radius> this.area_max){
            // this.theta gives normal to impact location
            // rotation of PI/2 gives the angle of reflection (of the circle's tangeante at this exact location)
            // if angle_speed is substracted, it gives alpha : angle
            // let alpha = this.theta + Math.PI / 2 - this.angle_speed;
            // this.angle_speed = this.theta + Math.PI/2 + alpha
            this.reflect_speed(true);
        }
        // else if (this.r - this.radius < this.area_min){
        else if (this.pos.mag() - this.radius < this.area_min){
            this.reflect_speed(false);
        }
        this.change_pos();
    }

    reflect_speed(out){
        this.impact.push([this.pos.x, this.pos.y]);
        // get speed before reflection:
        this.norm_speed = this.speed.mag();
        // to be changed:
        //out ?
        //    this.angle_speed = 2*(this.theta + Math.PI/2) - this.angle_speed :
        //    this.angle_speed =  (2*(this.theta + Math.PI/2) - this.angle_speed);
        // let normal = this.pos.copy();
        // Get the normal of reflect:
        let normal = this.pos.copy();
        normal.mult(-1);
        normal.normalize();
        this.speed.reflect(normal);
        //this.speed.set(r);
        //this.speed.x = this.norm_speed*Math.cos(this.angle_speed);
        //this.speed.y = this.norm_speed*Math.sin(this.angle_speed);
        // this.angle_speed = angleBetween(this.base_vect, this.speed)
    }

    is_pressed(X, Y){
        if(abs(this.pos.x-X)<this.radius && abs(this.pos.y-Y)<this.radius){
        // on-off switch:
        this.pressed = !this.pressed;
        }
    }
}
p5.Vector.prototype.reflect = function reflect(surfaceNormal) {
  surfaceNormal.normalize();
  return this.sub(surfaceNormal.mult(2 * this.dot(surfaceNormal)));
};