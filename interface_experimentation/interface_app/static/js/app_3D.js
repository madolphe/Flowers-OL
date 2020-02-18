let windowWidth = 1000;
let windowHeight = 600;
let windowDepth = 800;
let ball;
let app;

class Ball{
    constructor(color, radius_max, speed){
        this.x = random(-windowWidth/3,windowWidth/3);
        this.y = random(-windowHeight/3, windowHeight/3);
        this.z = random(-windowDepth/3, windowDepth/3);
        // Speed should be also negative at the beggining (messier)
        this.speedx = speed;
        this.speedy = speed;
        this.speedz = speed;
        console.log(this.x, this.y, this.z);
        this.radius = random(50, radius_max);
        this.color = color;
        this.display();
        this.contact = function(ball)
        {
            if((this.x == ball.x) && (this.y == ball.y) && (this.z == ball.z))
            {
                // Do something when there is a collision 
            }
        }
    }
    display(){
        push();
        fill(this.color);
        translate(this.x, this.y, this.z);
        // 24 is recommended by the docs (number of polygons for 3D)
        sphere(this.radius, 24, 24);
        pop();
    }
    move(){
        // Screen doesnt fit with the movement!
        if((this.x > windowWidth/3) || (this.x < -windowWidth/3)){this.speedx=-1*this.speedx}
        if((this.y > windowHeight/3) || (this.y < - windowHeight/3)){this.speedy=-1*this.speedy}
        if((this.z > windowDepth/3) || (this.z < -windowDepth/3)){this.speedz=-1*this.speedz}
        this.x += this.speedx;
        this.y += this.speedy;
        this.z += this.speedz;
    }
}

class App{
    constructor(n_targets, n_distractors, target_color, distractor_color){
        this.n_targets = n_targets;
        this.n_distractors = n_distractors;
        this.targets = [];
        this.distractors = [];
        this.frozen = true;
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Ball(target_color, 80, 3))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.distractors.push(new Ball(distractor_color, 80, 3))
        }
        this.display_balls = function(){
        // functions used to display all balls
        this.targets.forEach(function (item, index, array){item.display()});
        this.distractors.forEach(function (item, index, array){item.display()})
        };
        this.move_balls = function(){
            // functions used to display all balls
            if (!this.frozen){
                this.targets.forEach(function (item, index, array){item.move()});
                this.distractors.forEach(function (item, index, array){item.move()})
            }
        };
        this.details = function(){
            console.log(Object.keys(this))
        };
        this.change_color = function(){
            this.targets.forEach(function (item, index, array){item.color = 'grey'});
            this.distractors.forEach(function (item, index, array){item.color = 'grey'})
        };
    }
}

function setup(){
  createCanvas(windowWidth, windowHeight, WEBGL);
  ball = new Ball('yellow', 100, 1);
  app = new App(5, 5, 'yellow', 'red')
}

function draw(){
    background(100);
    noFill();
    box(windowWidth, windowHeight, windowDepth);
    //ball.display();
    //ball.move();
    app.change_color();
    app.display_balls();
    app.move_balls();
}
