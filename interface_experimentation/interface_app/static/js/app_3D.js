// @TODO: understand position and camera
// @TODO: add "hover" over balls
// @TODO: add json reader and launch the parameterized app from the outside


let windowWidth = 1200;
let windowHeight = 800;
let windowDepth = 600;

let boxWidth= windowWidth ;
let boxHeight = windowHeight ;
let boxDepth = windowDepth ;

// let ball;
let app;
let delta = 0; // camera angle for answering phase
let back = false; // variable used by camera to get back to initial position
let test;
// let scaling_factor_height;
let depth_origine;
// let scaling_factor_width;

class Ball{
    constructor(color, radius_max, speed, name){
        this.x = random(-0.5*boxWidth,0.5*boxWidth);
        this.y = random(-0.5*boxHeight, 0.5*boxHeight);
        this.z = random(-boxDepth, 0);
        // Speed should be also negative at the beggining (messier)
        this.speedx = speed;
        this.speedy = speed;
        this.speedz = speed;
        this.displayX = 0;
        this.displayY = 0;
        this.radius = random(50, radius_max);
        this.square_size = this.radius*sqrt(2)/2;
        //this.square_size=this.radius;
        this.color = color;
        this.display();
        this.name = name;
        this.hover = false;
    }

    scale(){
        var v = createVector(this.x, this.y, this.z);
        var p = screenPosition(v);
        this.displayX = p['x'];
        this.displayY = p['y'];
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
    display(mouseX, mouseY){
        if(!this.hover){
            push();
            fill(this.color);
            translate(this.x, this.y, this.z);
            // 24 is recommended by the docs (number of polygons for 3D)
            sphere(this.radius, 10, 10);
            pop()
        }else{
            this.scale();
            console.log(this.displayX, this.displayY);
            if(abs(this.displayX-mouseX)<this.radius && abs(this.displayY-mouseY)<this.radius){this.color = 'green';}
            push();
            fill(this.color);
            translate(this.x, this.y, this.z);
            // 24 is recommended by the docs (number of polygons for 3D)
            sphere(this.radius, 10, 10);
            pop()
        }
    }
    change_pos(){
        this.x += this.speedx;
        this.y += this.speedy;
        this.z += this.speedz;
    }
    move(){
        // Function to change direction (constraints on motion)
        // Screen doesnt fit with the movement!
        console.log(this.x-this.radius);
        console.log(boxWidth/2);
        if((this.x > 0.5*boxWidth) || (this.x < -0.5*boxWidth)){
            this.speedx=-1*this.speedx;
            this.change_pos()
        }
        if((this.y > 0.5*boxHeight) || (this.y < -0.5*boxHeight)){
            this.speedy=-1*this.speedy;
            this.change_pos()
        }
        if(((this.z) > 0.5*boxDepth) || ((this.z) < -0.5*boxDepth)){
            this.speedz=-1*this.speedz;
            this.change_pos()
        }
        this.change_pos();
    }
}

class App{
    constructor(n_targets, n_distractors, target_color, distractor_color){
        this.n_targets = n_targets;
        this.n_distractors = n_distractors;
        this.targets = [];
        this.distractors = [];
        this.frozen = false;
        this.turn = false;
        this.hover = false;
        setInterval(this.freeze_app, 1000);
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Ball(target_color, 100, 5, step))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.distractors.push(new Ball(distractor_color, 60, 5, step+this.n_targets))
        }
        this.all_objects = this.targets.concat(this.distractors);
    }
    freeze_app(){
        if(!this.frozen){
            this.frozen = true;
        }else{
            this.frozen = false;
        }
        // console.log(this.frozen);
    }
    move_balls(){
        // function used to display all balls
        // console.log(this.frozen);
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
        this.targets.forEach(function(item){item.color = 'red'});
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
}

function setup(){
    //tan function takes radians
    depth_origine = windowHeight/(2*tan(PI/6));
    console.log(depth_origine);
    depth_origine = 1090;
    createCanvas(windowWidth, windowHeight, WEBGL);
    addScreenPositionFunction();
    cam = createCamera();
    app = new App(4, 4, 'yellow', 'red');
    app.change_to_same_color();
    // check whether the timer could be incorporate to app!
    timer(app, 2000, 2000, 5000);
}
function timer(app, fixation_time, tracking_time, answer_time){
    setTimeout(function () {
        app.frozen = true;
        app.change_to_initial_color();
        setTimeout(function(){
            app.frozen = false;
            app.change_to_same_color();
            setTimeout(function(){
                app.frozen = true;
                app.turn = true;
                app.enable_hover();
                // launch app clickable
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

function draw(){
    perspective(PI/3.0, windowWidth/windowHeight, depth_origine/10, depth_origine*10.0);
    background(100);
    noFill();
    debugMode();
    // Default elements for perspective are fov: pi/3, ratio aspect: width/height, clipping plan 0.1 to 10*box_size
    // perspective(3.14/3, (windowWidth/windowHeight), eyeZ/10.0, eyeZ*10);
    // translate(0,0,-boxDepth/2);
    push();
    translate(0,0,-boxDepth/2);
    box(boxWidth, boxHeight, boxDepth);
    pop();
    app.check_collisions();
    app.display_balls(mouseX-600, mouseY-400);
    app.move_balls();
    spatial_rotation(app, delta);
}
