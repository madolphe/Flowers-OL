// @TODO : find position
// @TODO : get keyboard press for detection
// @TODO : display delta orientation

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
        this.pos = [0, 0];
        // mode
        this.display = false;
        this.other_objects = other_objects;
    }
    display_task(){
        this.find_position();
        if(this.display){
            push();
            imageMode(CENTER);
            translate(windowWidth/2, windowHeight/2);
            scale(0.1);
            image(this.image, 0, 0);
            pop();
        }
    }
    find_position(){
        // check for free location considering
    }
    timer_display(){
        setTimeout(this.restart.bind(this), this.RSI)
    }

    timer_pause(){
        setTimeout(this.start_display.bind(this), this.SRI_max)
    }
    keyboard_pressed(key_value){
    }

    start_display(){
        this.available_time -= this.SRI_max;
        if(this.available_time-this.RSI>0){
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

