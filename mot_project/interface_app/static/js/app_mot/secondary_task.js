// @TODO : get keyboard press for detection

class Secondary_Task{
    constructor(image, type, SRI_max, RSI, tracking_time, delta_orientation, other_objects){
        this.image = image;
        this.type = type;
        // duration of interval between presentation of sec task:
        this.SRI_max = SRI_max;
        // duration of display of sec task:
        this.RSI = RSI;
        this.delta_orientation = delta_orientation;
        this.tracking_time = tracking_time;
        // total number of secondary task presentation:
        this.available_time = this.tracking_time;
        // number of already displayed secondary task:
        this.index_pres = 0;
        // mode
        this.display = false;
        this.other_objects = other_objects;
        this.in_img_scaling = 0.1;
        this.results = []
    }
    find_position(){
        do {
            this.r = random(this.other_objects[0].area_min + this.other_objects[0].radius,
                this.other_objects[0].area_max - this.other_objects[0].radius);
            this.theta = random(0,2*Math.PI);
            this.x = Math.round(this.r*Math.cos(this.theta));
            this.y = Math.round(this.r*Math.sin(this.theta));
        } while(!this.is_free_position())
    }
    is_free_position(){
        // check for free location considering other objects
        this.other_objects.forEach(function(item){
            if (Math.sqrt((this.x - item.pos.x) ** 2 + (this.y - item.pos.y) ** 2) < item.radius) {
                return false;
            }
        }, this);
        return true
    }
    display_task(){
        if(this.display){
            push();
            imageMode(CENTER);
            translate(this.x + windowWidth/2, this.y + windowHeight/2);
            scale(0.15);
            image(this.image, 0, 0);
            pop();

            push();
            stroke('gold');
            strokeWeight(30);
            translate(this.x+ windowWidth/2,  this.y + windowHeight/2);
            scale(this.in_img_scaling);
            line(0,- this.image.height/2, 0, this.image.height/2);
            pop();
            // space btween branch is set to 1/6 of the image
            let space = this.in_img_scaling*this.image.height/6;
            let hypo = (this.in_img_scaling*this.image.width/4)*(1/Math.cos(radians(this.delta_orientation)));
            let opp = hypo*(Math.sin(radians(this.delta_orientation)));
            for(let i=0; i<5; i++){
                if((2-i)*space - opp < -this.in_img_scaling*this.image.height/2){
                    opp = -( -this.in_img_scaling*this.image.height/2 - (2-i)*space );
                    hypo = opp/(Math.sin(radians(this.delta_orientation)));
                }else{
                    hypo = (this.in_img_scaling*this.image.width/4)*(1/Math.cos(radians(this.delta_orientation)));
                    opp = hypo*(Math.sin(radians(this.delta_orientation)));
                }
                push();
                stroke('gold');
                strokeWeight(2);
                translate(this.x+ windowWidth/2,  this.y + windowHeight/2 + (2-i)*space);
                rotate(-radians(this.delta_orientation));
                // scale(0.07);
                line(0, 0, hypo, 0);
                pop();

                push();
                stroke('gold');
                strokeWeight(2);
                translate(this.x+ windowWidth/2,  this.y + windowHeight/2 + (2-i)*space);
                rotate(radians(this.delta_orientation));
                // scale(0.07);
                line(-hypo, 0, 0, 0);
                pop();
            }
        }
    }
    timer_display(){
        this.time_start_display = Date.now();
        this.timer_disp_id = setTimeout(this.restart.bind(this), this.RSI);
    }
    timer_pause(){
        this.timer_pause_id = setTimeout(this.start_display.bind(this), this.SRI_max)
    }
    keyboard_pressed(key_value){
        if(key_value==32){
            this.display = false;
            this.results.push([this.delta_orientation, Date.now() - this.time_start_display]);
            clearTimeout(this.timer_disp_id);
            this.available_time -= Date.now() - this.time_start_display;
            this.restart();
        }
    }
    start_display(){
        this.available_time -= this.SRI_max;
        if(this.available_time-this.RSI>0){
                this.find_position();
                this.display=true;
                this.timer_display();
        }
    }
    restart(){
        // after RSI
        if(this.display){
            // user has found object so it's not displayed anymore:
            this.display=false;
            this.available_time -= this.RSI;
            this.timer_pause();

        }else{
            this.available_time -= this.RSI;
            this.timer_pause();
        }
    }
}

