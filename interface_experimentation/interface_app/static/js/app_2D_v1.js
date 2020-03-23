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
        sessionStorage.setItem(this.name, [this.pressed, this.type]);
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
        sessionStorage.setItem(this.name, [this.pressed, this.type]);}
    }
}
class App{
    constructor(n_targets, n_distractors, target_color, distractor_color, boxWidth, boxHeight, radius_min,
                radius_max, speed_min, speed_max, hover_color)
    {
        this.boxWith = boxWidth;
        this.boxHeight = boxHeight;
        this.n_targets = n_targets;
        this.n_distractors = n_distractors;
        this.targets = [];
        this.distractors = [];
        this.frozen = false;
        this.hover = false;
        this.phase = 'init';
        this.speed_min = speed_min;
        this.speed_max = speed_max;
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Ball(target_color, radius_min, radius_max, this.speed_min, this.speed_max, step, boxWidth,
                boxHeight,'target', this.targets, hover_color))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.distractors.push(new Ball(distractor_color, radius_min, radius_max, this.speed_min, this.speed_max, step+this.n_targets,
            boxWidth, boxHeight, 'distractor', this.targets.concat(this.distractors), hover_color));
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
        if(this.phase=='got_response'){this.unselect_objects()} //all objects are getting unselected}
        this.targets.forEach(function(item){
            item.color = 'green';
            item.add_hover();
        });
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
        if(app.phase != 'got_response'){this.all_objects.forEach(function (item){item.is_pressed(mouseX, mouseY)})}
    }
    unselect_objects(){
        // this.all_objects.forEach(function (item){item.pressed = false});
        this.all_objects.forEach(function(item){item.pres = true;})
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
    hover_color = color(255, 255, 255);
    hover_color.setAlpha(200);
    app = new App(4, 4, 'red', 'yellow',
                   window_width, window_height, 90, 120, 4, 6, hover_color);
    app.change_to_same_color();
    // check whether the timer could be incorporate to app!
    timer(app, 2000, 2000, 5000);
}
function draw(){
    background(100);
    noFill();
    if(app.phase=='fixation'||app.phase == 'got_response'){app.change_to_initial_color()}
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
function answer_button_clicked(){
    if(document.getElementById("button_app").value == 'Next_episode' ){
        let params = {test: 'aha'};
        post('/', params, 'post')
    }else{
        if(document.getElementById("button_app").value == 'Answer' ){
            console.log("clicked");
            app.phase = 'got_response';
            app.frozen = true;
            document.getElementById("button_app").value = 'Next_episode';
        }
    }
}
function post(path, params, method='post') {
    // first create an hidden form:
    let form = document.getElementById('request');
    form.method = method;
    form.action = path;
    // Pass all parameters needed:
    for (const key in params) {
        if (params.hasOwnProperty(key)) {
          const hiddenField = document.createElement('input');
          hiddenField.type = 'hidden';
          hiddenField.name = key;
          hiddenField.value = params[key];
          form.appendChild(hiddenField)}
    }
    document.body.appendChild(form);
    form.submit();
}