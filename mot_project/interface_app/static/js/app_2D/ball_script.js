class Ball{
    constructor(color, radius_min, radius_max, speed_min, speed_max,
                name, boxWidth, boxHeight, type, forbidden_loc, hover_color){
        // Speed should be also negative at the beggining (messier)
        this.speedx =  random(speed_min, speed_max);
        this.speedy = random(speed_min, speed_max);
        // Inverse initial direction randomly:
        let sx = random(-1,1);
        let sy = random(-1,1);
        if(sx<0){this.speedx = -this.speedx}
        if(sy<0){this.speedy = -this.speedy}
        this.boxWidth = boxWidth;
        this.boxHeight = boxHeight;
        this.radius = random(radius_min, radius_max);
        this.square_size = this.radius;
        // We don't want our balls to overlap when initializing :
        let i = 0;
        this.init_mode = true;
        this.x = random(radius_max,boxWidth-radius_max);
        this.y = random(radius_max, boxHeight-radius_max);
        let number = 0;
        while (i<forbidden_loc.length) {
            // While we haven't found a location regarding to all already positioned balls
            this.contact(forbidden_loc[i]);
            if(this.init_mode){
                i=i+1;
            }
            else{
                number=number+1;
                i=0;
                this.init_mode=true;
                this.x = random(radius_max,boxWidth-radius_max);
                this.y = random(radius_max, boxHeight-radius_max)
            }
        }
        this.init_mode = false;
        this.color = color;
        this.display();
        this.name = name;
        this.hover = false;
        this.pressed = false;
        this.pres = false;
        this.type = type;
        this.x1 = 0;
        this.x2 = 0;
        this.y1 = 0;
        this.y2 = 0;
        this.hover_color = hover_color;
        sessionStorage.setItem(this.name, 0);
    }
    update_next_boundaries(){
        this.x1 = this.x + this.speedx - this.square_size/2;
        this.x2 = this.x + this.speedx + this.square_size/2;
        this.y1 = this.y + this.speedy - this.square_size/2;
        this.y2 = this.y + this.speedy + this.square_size/2;

    }
    contact(ball){
        this.update_next_boundaries();
        ball.update_next_boundaries();
         if(((this.x1  > ball.x1 )&&(this.x1 < ball.x2))
             ||((this.x2 > ball.x1)&&(this.x2 < ball.x2)))
         {
             // balls are aligned along x-axis, let's check y-axis:
             if((((this.y1  > ball.y1) && (this.y1  <ball.y2))) ||
                 ((this.y2  > ball.y1) && (this.y2  <ball.y2))){
                 if(!this.init_mode){
                    let sx =  Math.sign(ball.speedx);
                    let sy =  Math.sign(ball.speedy);
                    ball.speedx = Math.sign(this.speedx)*ball.speedx;
                    ball.speedy = Math.sign(this.speedy)*ball.speedy;
                    this.speedx = -sx*this.speedx;
                    this.speedy = -sy*this.speedy;
                 }else{
                     this.init_mode = false;
                 }
             }
         }
    }
    add_hover(){
        push();
        fill(this.hover_color);
        noStroke();
        // 24 is recommended by the docs (number of polygons for 3D)
        ellipse(this.x, this.y, 1.2*this.radius, 1.2*this.radius);
        pop();
    }
    display(X, Y){
        if(this.hover){
            if(this.pressed){
                if(!this.pres){
                    // Not the time to reveal yet:
                    this.color = 'green';
                    if(abs(this.x-X)<0.4*this.radius && abs(this.y-Y)<0.4*this.radius){
                        this.add_hover();
                        console.log(this.x1, this.x2, this.y1, this.y2);
                    }
                }else{
                    // Time to show answer!
                    if(this.type == 'target'){
                        // user has clicked, well done
                        this.color = 'green';
                        this.add_hover();
                    }else{
                        // user should have clicked but missed
                        this.color = 'yellow';
                    }
                }
            }
            else{
                if(!this.pres){
                    // If this is not reveal time:
                    this.color = 'yellow';
                    if(abs(this.x-X)<0.4*this.radius && abs(this.y-Y)<0.4*this.radius) {
                        this.add_hover();
                    }
                }else{
                    // Time to show answer:
                    if(this.type=='target'){
                        // user should have clicked on this one but missed it:
                        this.color = 'red';
                        //this.add_hover();
                    }else{
                        this.color = 'yellow';
                    }
                }
            }
        }
        push();
        fill(this.color);
        ellipse(this.x, this.y, this.radius, this.radius);
        pop();
    }
    change_pos(){
        this.x += this.speedx;
        this.y += this.speedy;
    }
    move(){
        this.change_pos();
        // Function to change direction (constraints on motion)
        if(((this.x + this.radius/2) > this.boxWidth) || ((this.x - this.radius/2) < 0)){
            this.speedx=-1*this.speedx;
            this.change_pos()
        }
        if(((this.y + this.radius/2) > this.boxHeight) || ((this.y - this.radius/2) < 0)){
            this.speedy=-1*this.speedy;
            this.change_pos()
        }
    }
    is_pressed(X, Y){
        if(abs(this.x-X)<0.4*this.radius && abs(this.y-Y)<0.4*this.radius){
        // on-off switch:
        this.pressed = !this.pressed;
        }
    }
}
