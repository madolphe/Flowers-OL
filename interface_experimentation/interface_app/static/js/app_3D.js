let windowWidth = 1000;
let windowHeight = 600;
let windowDepth = 800;
let ball;

class Ball{
    constructor(color, radius_max){
        this.x = random(-windowWidth,windowWidth);
        this.y = random(-windowHeight, windowHeight);
        this.z = random(-windowDepth, windowDepth);
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
  ball = new Ball('yellow', 100, 24, 24);

}

function draw() {
    background(100);
    noFill();
    box(windowWidth, windowHeight, windowDepth);
    ball.display();
}
