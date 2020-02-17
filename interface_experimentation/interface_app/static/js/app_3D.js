let windowWidth = 1000;
let windowHeight = 600;
let windowDepth = 800;
let ball;

class Ball{
    constructor(color, radius_max, speed){
        this.x = random(-windowWidth/2,windowWidth/2);
        this.y = random(-windowHeight/2, windowHeight/2);
        this.z = random(-windowDepth/2, windowDepth/2);
        this.speedx = speed;
        this.speedy = speed;
        this.speedz = speed;
        console.log(this.x, this.y, this.z);
        this.radius = random(radius_max);
        this.color = color;
    }
    display(){
        push();
        translate(this.x, this.y, this.z);
        //translate(0, 0, 0);
        fill(this.color);
        // 24 is recommended by the docs (number of polygons for 3D)
        sphere(this.radius, 24, 24);
        pop();
    }
    move(){
        // Screen doesnt fit with the movement!
        if((this.x > windowHeight/2) || (this.x < -windowHeight/2)){this.speedx=-this.speedx}
        if((this.y > windowWidth/2) || (this.y < -windowWidth/2)){this.speedy=-this.speedy}
        if((this.z > windowDepth/2) || (this.z < -windowDepth/2)){this.speedz=-this.speedz}
        this.x = this.x + this.speedx;
        this.y = this.y + this.speedy;
        this.z = this.z + this.speedz;
    }
}

class App{
    constructor(n_targets, n_distractors, target_color, distractor_color){
        this.n_targets = n_targets;
        this.n_distractors = n_distractors;
        this.targets = [];
        this.distractors = [];
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Ball(target_color))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.targets.push(new Ball(distractor_color))
        }
    }
    details(){
        console.log(Object.keys(this))
    }
    display_balls(){
        // functions used to display all balls
    }
    move_balls(){
        // function used to move all balls
    }
}

function setup() {
  createCanvas(windowWidth, windowHeight, WEBGL);
  ball = new Ball('yellow', 100, 1);

}

function draw() {
    background(100);
    noFill();
    box(windowWidth, windowHeight, windowDepth);
    ball.move();
    ball.display();

}
