// @TODO: add button to send results
// @TODO: fill json with results
// @TODO: add json reader and launch the parameterized app from the outside

// Variables needed for object in canvas:
let window_width;
let window_height;
let window_depth;
let boxWidth;
let boxHeight;
let boxDepth;
let depth_origine;
let canvas;
let cam;
let hover_color;
let app;
let delta = 0; // camera angle for answering phase
let back = false; // variable used by camera to get back to initial position

// clear session storage:
sessionStorage.clear();

class Ball{
    constructor(color, radius_min, radius_max, speed, name, boxWidth, boxHeight, boxDepth, type){
        this.boxDepth = boxDepth;
        this.boxWidth = boxWidth;
        this.boxHeight = boxHeight;
        this.x = random(-0.5*boxWidth,0.5*boxWidth);
        this.y = random(-0.5*boxHeight, 0.5*boxHeight);
        this.z = random(-boxDepth, 0);
        // Speed should be also negative at the beggining (messier)
        this.speedx = speed;
        this.speedy = speed;
        this.speedz = speed;
        this.displayX = 0;
        this.displayY = 0;
        this.radius = random(radius_min, radius_max);
        this.square_size = this.radius*sqrt(2)/2;
        //this.square_size=this.radius;
        this.color = color;
        this.display();
        this.name = name;
        this.hover = false;
        this.pressed = false;
        this.type  = type;
        sessionStorage.setItem(this.name, [this.pressed, this.type]);
    }

    position_on_screen(){
        let vect = createVector(this.x, this.y, this.z);
        let position = screenPosition(vect);
        this.displayX = position['x'];
        this.displayY = position['y'];
    }
    contact(ball){
         let x1 = this.x - this.square_size;
         let x2 = this.x + this.square_size;
         let y1 = this.y + this.square_size;
         let y2 = this.y + this.square_size;
         let z1 = this.z + this.square_size;
         let z2 = this.z + this.square_size;
         if((((x1 - (ball.x - this.square_size)) > 0) && ((x1 - (ball.x + this.square_size))<0))||
             (((x2 - (ball.x - this.square_size)) > 0) && ((x2 - (ball.x + this.square_size))<0))){
             // balls are aligned along x-axis, let's check y-axis:
             if((((y1 - (ball.y - this.square_size)) > 0) && ((y1 - (ball.y + this.square_size))<0))||
             (((y2 - (ball.y - this.square_size)) > 0) && ((y2 - (ball.y + this.square_size))<0))){
                // balls are aligned along y-axis, let's check z-axis:
                 if((((z1 - (ball.z - this.square_size)) > 0) && ((z1 - (ball.z + this.square_size))<0))||
                    (((z2 - (ball.z - this.square_size)) > 0) && ((z2 - (ball.z + this.square_size))<0))){
                     ball.speedx = -ball.speedx;
                     ball.speedy = -ball.speedy;
                     ball.speedz = -ball.speedz;
                     this.speedx = -this.speedx;
                     this.speedy = -this.speedy;
                     this.speedz = -this.speedz;
                 }
             }
         }
    }
    add_hover(){
        //this.color = 'red'
        push();
        fill(hover_color);
        noStroke();
        translate(this.x, this.y, this.z);
        // 24 is recommended by the docs (number of polygons for 3D)
        sphere(this.radius+10, 10, 10);
        pop();
    }
    display(X, Y){
        if(this.hover){
            if(this.pressed){
                this.color = 'red';
                if(abs(this.displayX-X)<0.4*this.radius && abs(this.displayY-Y)<0.4*this.radius) {
                    this.add_hover();
                }
            }else{
                this.color = 'yellow';
                if(abs(this.displayX-X)<0.4*this.radius && abs(this.displayY-Y)<0.4*this.radius) {
                    this.add_hover();
                }
            }
        }
        push();
        fill(this.color);
        translate(this.x, this.y, this.z);
        // 24 is recommended by the docs (number of polygons for 3D)
        // sphere(this.radius, 10, 10);
        //fill(250, 100, 100); // For effect
        noStroke();
        ambientMaterial(175);
        scale(0.1*this.radius);
        model(virus);
        pop()
    }
    change_pos(){
        this.x += this.speedx;
        this.y += this.speedy;
        this.z += this.speedz;
    }
    move(){
        // Function to change direction (constraints on motion)
        // Screen doesnt fit with the movement!
        if(((this.x + this.radius) > this.boxWidth/2) || ((this.x - this.radius) < -this.boxWidth/2)){
            this.speedx=-1*this.speedx;
            this.change_pos()
        }
        if(((this.y + this.radius) > this.boxHeight/2) || ((this.y - this.radius) < -this.boxHeight/2)){
            this.speedy=-1*this.speedy;
            this.change_pos()
        }
        if(((this.z+this.radius) > this.boxDepth) || ((this.z-this.radius) < 0)){
            this.speedz=-1*this.speedz;
            this.change_pos()
        }
        this.change_pos();
    }
    is_pressed(X, Y){
        this.position_on_screen();
        if(abs(this.displayX-X)<0.4*this.radius && abs(this.displayY-Y)<0.4*this.radius){
            // on-off switch:
            this.pressed = !this.pressed;
            sessionStorage.setItem(this.name, [this.pressed, this.type]);
        }
    }
}
class App{
    constructor(n_targets, n_distractors, target_color, distractor_color, boxWidth, boxHeight, boxDepth){
        this.boxDepth = boxDepth;
        this.boxWith = boxWidth;
        this.boxHeight = boxHeight;
        this.n_targets = n_targets;
        this.n_distractors = n_distractors;
        this.targets = [];
        this.distractors = [];
        this.frozen = false;
        this.turn = false;
        this.hover = false;
        this.phase = 'init';
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Ball(target_color, 10, 10, 3, step, boxWidth, boxHeight, boxDepth,
                'target'))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.distractors.push(new Ball(distractor_color, 10, 10, 3, step+this.n_targets,
                boxWidth, boxHeight, boxDepth, 'distractor'))
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
        this.targets.forEach(function(item){item.add_hover();item.color = 'red'});
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
            for (let j=i ; j< this.all_objects.length; j++){
                this.all_objects[i].contact(this.all_objects[j]);
            }
        }
    }
    check_mouse_pressed(mouseX, mouseY){
        console.log("get in app check mouse pressed");
        this.all_objects.forEach(function (item){
            item.is_pressed(mouseX, mouseY)
        });
    }
}

function preload() {
  // Load model with normalise parameter set to true
  virus = loadModel('/static/js/microbe.obj', true);
}

function setup(){
    window_depth = 600;
    window_height = 0.9*windowHeight;
    window_width = 0.9*windowWidth;
    boxWidth= window_width ;
    boxHeight = window_height ;
    boxDepth = window_depth;
    //tan function takes radians
    depth_origine = window_height/(2*tan(PI/6));
    canvas = createCanvas(window_width, window_height, WEBGL);
    canvas.parent('app_holder');
    addScreenPositionFunction();
    cam = createCamera();
    app = new App(4, 4, 'yellow', 'red', boxWidth, boxHeight, boxDepth);
    app.change_to_same_color();
    // check whether the timer could be incorporate to app!
    timer(app, 2000, 2000, 5000);
    hover_color = color(255, 255, 255);
    hover_color.setAlpha(80);
}
function draw(){
    ambientLight(60, 60, 60);
    pointLight(255, 255, 255, 0, 0, 100);
    perspective(PI/3.0, window_width/window_height, depth_origine/10, depth_origine*10.0);
    background(100);
    noFill();
    // Default elements for perspective are fov: pi/3, ratio aspect: width/height, clipping plan 0.1 to 10*box_size
    // perspective(3.14/3, (window_width/window_height), eyeZ/10.0, eyeZ*10);
    // translate(0,0,-boxDepth/2);
    push();
    translate(0,0,-boxDepth/2);
    strokeWeight(4);
    stroke(250, 0, 0);
    box(window_width, window_height, boxDepth);
    pop();
    if(app.frozen && app.phase=='fixation'){app.change_to_initial_color();}
    app.check_collisions();
    app.display_balls(mouseX-(window_width/2), mouseY-(window_height/2));
    app.move_balls();
    spatial_rotation(app, delta);
}
function mousePressed(event) {
   // First test if objects are in "clickable mode"
   if (app.distractors[0].hover) {
       app.check_mouse_pressed(mouseX-(window_width/2), mouseY-(window_height/2));
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
                app.turn = true;
                app.enable_hover();
                show_button();
                },answer_time)
        }, tracking_time)
    }, fixation_time);
}
function spatial_rotation(app){
        if((app.turn)&&delta>=0){
        if (!back){
            delta += 0.002;
            cam.pan(0.002);
            cam.move(2.2,0,-0.26);
        }else{
            delta -= 0.01;
            cam.pan(-0.01);
            cam.move(-11,0,1.3);
        }
        if(delta > 0.8){
            cam.move(0, 0, 0);
            back =true;
        }
    }
}
function windowResized(){
      createCanvas(0.9*windowWidth, 0.9*windowHeight);
}
function show_button(){
    document.getElementById("button_app").type = 'submit';
}
function test(){
    let POST_request = '';
    let tmp = document.getElementById("button_request").action;
    document.getElementById("button_request").action = tmp + POST_request;
}