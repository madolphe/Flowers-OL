class Tracked_Object {
    // INIT FUNCTIONS //
    constructor(speed_min, speed_max, name, area_min, area_max, type, forbidden_loc, radius, positions) {
        this.radius = radius; // in pixels
        // initial speed
        this.speedx = Math.round(Math.random()) > 0 ? random(speed_min, speed_max) : random(-speed_min, -speed_max);
        this.speedy = Math.round(Math.random()) > 0 ? random(speed_min, speed_max) : random(-speed_min, -speed_max);
        // speed_max and speed_min are given in deg par seconde
        // As FPS = 60 and 1 deg = 1 ppd:
        this.speedx = this.speedx * ppd / fps;
        this.speedy = this.speedy * ppd / fps;
        // Create a velocity vector
        this.speed = createVector(this.speedx, this.speedy);
        this.base_vect = createVector(1, 0);
        this.angle_speed = this.base_vect.angleBetween(this.speed);

        // Boundaries:
        this.area_min = area_min; // in pixels
        this.area_max = area_max; // in pixels

        // We don't want our objects to overlap when initializing :
        //this.initial_position(forbidden_loc);
        this.init_pos(forbidden_loc, positions);

        this.name = name;
        // bool to check if user can start interracting with object:
        this.interact_phase = false;
        // bool to save if an object has been selected:
        this.pressed = false;

        this.answer = false;
        this.type = type;
        this.pos_next = createVector(0, 0);
        this.impact = [[this.x, this.y]];
        // All objects (target or distractors) are init in white
        this.color = 'white';
        this.color_colision = 'black';
    }

    init_pos(forbidden_loc, positions) {
        let search = false;
        while (!search) {
            let idx = parseInt(random(0, positions.length));
            var param = positions[idx];
            console.log(param);
            this.r = positions[idx][1];
            this.theta = Math.PI * positions[idx][0] / 180;
            this.index = idx;
            this.x = Math.round(this.r * Math.cos(this.theta));
            this.y = Math.round(this.r * Math.sin(this.theta));
            this.pos = createVector(this.x, this.y);
            search = true;
            forbidden_loc.forEach(function (item) {
                if (item.index == idx) {
                    search = false;
                }
            });
        }
    }

    // 1_ DISPLAY OBJECT (CURRENT LOCATION)//
    add_hover() {
        push();
        translate(this.x, this.y);
        fill('red');
        ellipse(0, 0, this.radius, this.radius);
        pop();
    }

    display(X, Y) {
        this.event_display(X, Y);
        push();
        strokeWeight(2);
        stroke(this.color);
        noFill();
        // Poisition isn't translated to the center of the canvas, we do it when displaying:
        line(this.pos.x - this.radius / 2 + windowWidth / 2,
            this.pos.y + windowHeight / 2,
            this.pos.x + this.radius / 2 + windowWidth / 2,
            this.pos.y + windowHeight / 2);
        line(this.pos.x + windowWidth / 2,
            this.pos.y - this.radius / 2 + windowHeight / 2,
            this.pos.x + windowWidth / 2,
            this.pos.y + this.radius / 2 + windowHeight / 2);
        ellipse(this.pos.x + windowWidth / 2, this.pos.y + windowHeight / 2, 2 * this.radius);
        pop();
        this.display_speed();
    }

    display_speed() {
        // theta between 0 and 2PI
        // this.event_display(X, Y);
        push();
        fill(this.color);
        rectMode(CENTER);
        textSize(12);
        text(this.name, this.pos.x + 12 + windowWidth / 2, this.pos.y + 12 + windowHeight / 2);
        pop();
        push();
        stroke(this.color);
        strokeWeight(3);
        pop();
        push();
        textSize(11);
        fill(this.color);
        text('ang speed:   ' + (degrees(this.angle_speed).toFixed(2)).toString(),
            this.pos.x - 22 + windowWidth / 2, this.pos.y - 55 + windowHeight / 2);

        text('R:   ' + Math.round(this.pos.mag()).toString(),
            this.pos.x - 22 + windowWidth / 2, this.pos.y - 45 + windowHeight / 2);
        text('Theta:   ' + ((degrees(this.base_vect.angleBetween(this.pos)) % 360).toFixed(2)).toString(),
            this.pos.x - 22 + windowWidth / 2, this.pos.y - 35 + windowHeight / 2);

        text('Speedx:  ' + this.speed.x.toFixed(2).toString(),
            this.pos.x - 22 + windowWidth / 2, this.pos.y - 25 + windowHeight / 2);

        text('Speedy:  ' + this.speed.y.toFixed(2).toString(),
            this.pos.x - 22 + windowWidth / 2, this.pos.y - 15 + windowHeight / 2);
        pop();
        let disp_pos = this.pos.copy();
        disp_pos.normalize();
        // display
        this.drawArrow(this.pos, disp_pos, 'red');
        // display theta direction:
        this.drawArrow(this.pos, this.speed, 'green');
        // display trajectories:
        pop();
        if (this.impact.length > 2) {
            let i = 0;
            while (i < this.impact.length - 1) {
                fill('red');
                ellipse(this.impact[i][0] + windowWidth / 2, this.impact[i][1] + windowHeight / 2, 10);
                stroke('white');
                line(this.impact[i][0] + windowWidth / 2, this.impact[i][1] + windowHeight / 2,
                    this.impact[i + 1][0] + windowWidth / 2, this.impact[i + 1][1] + windowHeight / 2);
                i++;
            }
        }
        push();
    }

    event_display(X, Y) {
        if (this.interact_phase) {
            if (this.pressed) {
                this.color = 'green';
            } else {
                this.color = 'white';
                if (abs((this.pos.x + windowWidth / 2) - X) < this.radius / 2 && abs((this.pos.y + windowHeight / 2) - Y) < this.radius / 2) {
                    this.color = 'green'
                }
            }
        }
    }

    // draw an arrow for a vector at a given base position
    drawArrow(base, vec, myColor) {
        push();
        stroke(myColor);
        strokeWeight(3);
        fill(myColor);
        translate(base.x + windowWidth / 2, base.y + windowHeight / 2);
        line(0, 0, 20 * vec.x, 20 * vec.y);
        rotate(this.base_vect.angleBetween(vec) % (Math.PI * 2));
        let arrowSize = 7;
        translate(20 * vec.mag(), 0);
        triangle(0, arrowSize / 2, 0, -arrowSize / 2, arrowSize, 0);
        pop();
    }

    is_pressed(X, Y) {
        // function called each time user press
        if (abs((this.pos.x + windowWidth / 2) - X) < this.radius && abs((this.pos.y + windowHeight / 2) - Y) < this.radius) {
            // on-off switch:
            this.pressed = !this.pressed;
        }
    }


    // 2_ FIND NEW POSITION: //
    // 2_1 RANDOM VARIATION AROUND PAST SPEED //
    speed_random_variation() {
        this.angle_speed = this.base_vect.angleBetween(this.speed);
        // let deviation = randomGaussian(this.angle_speed, 0.15);
        // this.speed.rotate(this.angle_speed-deviation);
        if (this.pos.mag() < this.area_max - 2 * this.radius && this.pos.mag() > this.area_min + 2 * this.radius) {
            this.speed.rotate(randomGaussian(0, 0.2));
            this.color_colision = 'green';
        } else {
            this.color_colision = 'black';
        }
    }

    // 2_2 CHECK COLLISIONS ACCORDING TO SPEED //
    contact(object) {
        // Update boundaries according to current speed vector:
        this.update_next_boundaries();
        object.update_next_boundaries();
        // Check if there is a collision:
        if (this.check_collision(object)) {
            // EXCHANGE SPEED:
            let sx = object.speed.x;
            let sy = object.speed.y;
            object.speed.x = this.speed.x;
            object.speed.y = this.speed.y;
            this.speed.x = sx;
            this.speed.y = sy;
            return true
        }
        return false
    }

    // Update next_position to check that next pos is ok :
    update_next_boundaries() {
        this.pos_next.x = this.pos.x + this.speed.x;
        this.pos_next.y = this.pos.y + this.speed.y;
    }

    check_collision(object) {
        // returns true if object is in contact with an other one
        return (dist(this.pos_next.x, this.pos_next.y, object.pos_next.x, object.pos_next.y) < 2 * this.radius)
    }

    // 2_3 CHECK THAT OBJECT ISN'T OUT OF THE SCENE//
    // Bouncing on imaginary non orthogonal walls:
    check_limits() {
        // Function to change direction (constraints on motion)
        if (this.pos.mag() + this.radius > this.area_max || this.pos.mag() - this.radius < this.area_min) {
            this.reflect_speed();
        }
    }

    reflect_speed() {
        // Get the normal of reflect:
        let normal = this.pos.copy();
        // pos points from origin to ext, reverse the vect:
        normal.mult(-1);
        // normal.normalize();
        this.speed.reflect(normal);
    }


    // 3_ MOVE OBJECTS //
    move() {
        this.pos.add(this.speed);
        this.theta = this.base_vect.angleBetween(this.pos);
    }
}

