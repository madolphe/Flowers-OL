class progressBar{
    constructor(idx_active_item){
        this.color = "blue";
        this.nb_ticks = 8;
        this.box_width = 350;
        this.box_height = 50;
        this.step_size = this.box_width / (this.nb_ticks + 1);
        this.box_x = 10 + this.step_size;
        this.box_y = 30;
        this.circle_diameter = 24;
        this.middle_box_y = this.box_y + this.box_height/2 ;
        this.progress_bar_width = 6;
        this.idx_active_item = idx_active_item;
        this.x_active_item = this.box_x + (this.idx_active_item)*this.step_size;
        this.triangle_height = 15;
        this.triangle_width = 10;
        this.stroke_weight = 0;
        this.percentage = parseInt(100 * this.idx_active_item / this.nb_ticks );
        this.percentage_text = this.percentage + "% ";
        this.margin_text = 5;
    }
    draw(){
        this.draw_backbone_bar();
        this.draw_circles();
        this.draw_active_task();
        this.draw_text();
    }
    draw_background(){
        push();
        fill('rgba(255,255,255,0.1)');
        rectMode(CORNERS);
        noStroke();
        rect(this.box_x, this.box_y - this.box_height/2 , this.box_x + this.box_width + 1.5*this.step_size, this.box_y + (3/2)*this.box_height);
        pop();
    }
    draw_text(){
        push();
        textSize(19);
        textAlign(CENTER, CENTER);
        text(this.percentage_text, this.box_x + this.box_width - this.step_size, this.middle_box_y);
        pop();
    }
    draw_circles(){
        for(let i=0; i<this.nb_ticks; i++){
            push();
            if(i<this.idx_active_item){
                fill('green');
                imageMode(CENTER);
                image(success, this.box_x + i*this.step_size, this.middle_box_y, this.circle_diameter, this.circle_diameter);
            }else{
                fill('darkgrey');
                strokeWeight(this.stroke_weight)
                ellipse(this.box_x + i*this.step_size, this.middle_box_y, this.circle_diameter);
            }
            pop();
        }
    }
    draw_backbone_bar(){
        push();
        rectMode(CORNERS);
        strokeWeight(this.stroke_weight);
        fill("#25ae88");
        rect(this.box_x, this.middle_box_y-this.progress_bar_width/2,
             this.box_x + this.step_size * (this.idx_active_item ), this.middle_box_y+this.progress_bar_width/2)
        pop();
        push();
        rectMode(CORNERS);
        fill('darkgrey');
        strokeWeight(this.stroke_weight);
        rect(this.box_x  + this.step_size * (this.idx_active_item), this.middle_box_y-this.progress_bar_width/2,
             this.box_x + this.box_width - 2*this.step_size, this.middle_box_y+this.progress_bar_width/2)
        pop();
    }
    draw_active_task(){
        push();
        strokeWeight(1);
        triangle(this.x_active_item, this.box_y,
                this.x_active_item - this.triangle_width, this.box_y - this.triangle_height,
                this.x_active_item + this.triangle_width, this.box_y - this.triangle_height)
        pop();
    }
}