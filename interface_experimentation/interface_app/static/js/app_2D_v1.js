// @TODO: add button to send results
// @TODO: fill json with results
// @TODO: add json reader and launch the parameterized app from the outside

// Variables needed for object in canvas:
let window_width;
let window_height;
let canvas;
let hover_color;
let app;
let delta = 0; // camera angle for answering phase
let back = false; // variable used by camera to get back to initial position
let answer_phase = false;
// clear session storage:
sessionStorage.clear();

class Ball{
    constructor(color, radius_min, radius_max, speed, name, boxWidth, boxHeight, type, forbidden_loc){

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
        console.log("Nombre de fois recommencé:", number);
        this.init_mode = false;
        // Speed should be also negative at the beggining (messier)
        let sx = random(-1,1);
        let sy = random(-1,1);

        if(sx<0){this.speedx = -speed}else{this.speedx=speed}
        if(sy<0){this.speedy = -speed}else{this.speedy=speed}
        this.speedy = speed;
        //this.square_size=this.radius;
        this.color = color;
        this.display();
        this.name = name;
        this.hover = false;
        this.pressed = false;
        this.type = type;
        this.x1 = 0;
        this.x2 = 0;
        this.y1 = 0;
        this.y2 = 0;
        this.display(2,2);
        sessionStorage.setItem(this.name, [this.pressed, this.type]);
    }
    update_boundaries(){
        this.x1 = this.x - this.square_size/2;
        this.x2 = this.x + this.square_size/2;
        this.y1 = this.y - this.square_size/2;
        this.y2 = this.y + this.square_size/2;
    }
    contact(ball){
        this.update_boundaries();
        ball.update_boundaries();
         if(((this.x1 > ball.x1 )&&(this.x1 < ball.x2))
             ||((this.x2 > ball.x1)&&(this.x2 < ball.x2)))
         {
             // balls are aligned along x-axis, let's check y-axis:
             if((((this.y1  > ball.y1) && (this.y1  <ball.y2))) ||
                 ((this.y2  > ball.y1) && (this.y2  <ball.y2))){
                 if(this.name == 0){
                     console.log(ball.name, this.name);
                 }
                 if(!this.init_mode){
                    ball.speedx = -ball.speedx;
                    ball.speedy = -ball.speedy;
                    this.speedx = -this.speedx;
                    this.speedy = -this.speedy;
                 }else{
                     this.init_mode = false;
                 }
             }
         }
    }
    add_hover(){
        push();
        fill(hover_color);
        noStroke();
        // 24 is recommended by the docs (number of polygons for 3D)
        ellipse(this.x, this.y, this.radius+10, this.radius+10);
        pop();
    }
    display(X, Y){
        if(this.hover){
            if(this.pressed){
                this.color = 'red';
                if(abs(this.x-X)<0.4*this.radius && abs(this.y-Y)<0.4*this.radius){
                        this.add_hover();
                        console.log(this.x1, this.x2, this.y1, this.y2);
                }
            }
            else{
                this.color = 'yellow';
                if(abs(this.x-X)<0.4*this.radius && abs(this.y-Y)<0.4*this.radius) {
                    this.add_hover();
                }
            }
        }
        push();
        // 24 is recommended by the docs (number of polygons for 3D)
        if(this.name == 0){this.color = 'green'};
        fill(this.color);
        ellipse(this.x, this.y, this.radius, this.radius);
        // rectMode(CENTER);
        //square(this.x, this.y, this.square_size);
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
        sessionStorage.setItem(this.name, [this.pressed, this.type]);}
    }
}
class App{
    constructor(n_targets, n_distractors, target_color, distractor_color, boxWidth, boxHeight, radius_min, radius_max, speed){
        this.boxWith = boxWidth;
        this.boxHeight = boxHeight;
        this.n_targets = n_targets;
        this.n_distractors = n_distractors;
        this.targets = [];
        this.distractors = [];
        this.frozen = false;
        this.hover = false;
        this.phase = 'init';
        this.speed = speed;
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Ball(target_color, radius_min, radius_max, speed, step, boxWidth,
                boxHeight,'target', this.targets))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.distractors.push(new Ball(distractor_color, radius_min, radius_max, speed, step+this.n_targets,
            boxWidth, boxHeight, 'distractor', this.targets.concat(this.distractors)));
        }
        this.all_objects = this.targets.concat(this.distractors);
    }
    freeze_app(){
        this.frozen = !this.frozen;
    }
    move_balls(){
        // function used to display all balls
        if (!this.frozen){
            this.all_objects.forEach(function (item){item.move()});
        }
    }
    details(){
        console.log(this.frozen)
    }
    change_to_same_color(){
        this.all_objects.forEach(function (item){item.color = 'yellow'});
    }
    change_to_initial_color(){
        this.targets.forEach(function(item){item.color = 'red'; item.add_hover();});
        this.distractors.forEach(function(item){item.color = 'yellow'});
    }
    display_balls(mouseX, mouseY){
        // function used to display all balls
        this.all_objects.forEach(function (item){item.display(mouseX, mouseY)});
    }
    enable_hover(){
        this.all_objects.forEach(function (item){item.hover = true});
    }
    check_collisions(){
        for(let i =0; i< this.all_objects.length; i++){
            for (let j=0 ; j< this.all_objects.length; j++){
                if(j!=i){
                    this.all_objects[i].contact(this.all_objects[j]);
                }
            }
        }
    }
    check_mouse_pressed(mouseX, mouseY){
        this.all_objects.forEach(function (item){
            item.is_pressed(mouseX, mouseY)
        });
    }
}
function preload() {
  // Load model with normalise parameter set to true
}
function setup(){
    window_height = 0.9*windowHeight;
    window_width = 0.9*windowWidth;
    canvas = createCanvas(window_width, window_height);
    canvas.parent('app_holder');
    app = new App(4, 4, 'yellow', 'red',
                   window_width, window_height, 90, 120, 3);
    app.change_to_same_color();
    // check whether the timer could be incorporate to app!
    timer(app, 2000, 2000, 5000);
    hover_color = color(255, 255, 255);
    hover_color.setAlpha(80);
}
function draw(){
    background(100);
    noFill();
    if(app.frozen && app.phase=='fixation'){app.change_to_initial_color()}
    app.display_balls(mouseX, mouseY);
    app.check_collisions();
    app.move_balls();
}
function mousePressed(event) {
   // First test if objects are in "clickable mode"
   if (app.distractors[0].hover) {
       app.check_mouse_pressed(mouseX, mouseY);
   }
}
function timer(app, fixation_time, tracking_time, answer_time){
    setTimeout(function () {
        app.phase = 'fixation';
        app.frozen = true;
        app.change_to_initial_color();
        setTimeout(function(){
            app.phase = 'tracking';
            app.frozen = false;
            app.change_to_same_color();
            setTimeout(function(){
                app.phase = 'answer';
                app.frozen = true;
                app.enable_hover();
                show_answer_button();
                },answer_time)
        }, tracking_time)
    }, fixation_time);
}
function windowResized(){
      createCanvas(0.9*windowWidth, 0.9*windowHeight);
}
function show_answer_button(){
    document.getElementById("button_app").type = 'submit';
}
function test(){
    let POST_request = '';
    let tmp = document.getElementById("button_request").action;
    document.getElementById("button_request").action = tmp + POST_request;
}
function answer_button_clicked(){
    if(document.getElementById("button_app").value == 'Answer' ){
        console.log("clicked");
        app.phase = 'fixation';
        app.frozen = true;
        document.getElementById("button_app").value = 'Next episode';
    }
}