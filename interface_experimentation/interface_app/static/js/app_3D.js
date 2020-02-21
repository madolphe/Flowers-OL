// @TODO: add app.timer to share all parts of the experiment
// @TODO: add clickable state of balls so that user can respond
// @TODO: add json reader and launch the parameterized app from the outside


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
        this.radius = random(50, radius_max);
        this.square_size = this.radius*sqrt(2)/2;
        this.square_size=this.radius/2;
        this.color = color;
        this.display();
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
        this.frozen = false;
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Ball(target_color, 40, 3))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.distractors.push(new Ball(distractor_color, 40, 3))
        }
        this.all_objects = this.targets.concat(this.distractors);
    }
    move_balls(){
        // function used to display all balls
        if (!this.frozen){
            this.all_objects.forEach(function (item){item.move()});
        }
    }
    details(){
        console.log(Object.keys(this))
    }
    change_color(){
        this.all_objects.forEach(function (item){item.color = 'yellow'});
    }
    display_balls(){
        // function used to display all balls
        this.all_objects.forEach(function (item){item.display()});
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
  createCanvas(windowWidth, windowHeight, WEBGL);
  app = new App(5, 5, 'yellow', 'red')
}

function draw(){
    background(100);
    noFill();
    box(windowWidth, windowHeight, windowDepth);
    //ball.display();
    //ball.move();
    app.change_color();
    app.check_collisions();
    app.display_balls();
    app.move_balls();
}
