let bug1; // Declare objects
let bug2;
let bug3;
let bug4;
let bug5;
let bug6;
let bug7;
let bug8;
let freeze = false;
let new_app;

setInterval(freeze_app, 10000);
function freeze_app(){
    freeze = true;
}

function setup() {
  createCanvas(710, 400);
  // Create object
    new_app = new App(10,12, "red", "blue");
    new_app.details();
    bug1 = new Jitter('red');
    bug2 = new Jitter('red');
    bug3 = new Jitter('red');
    bug4 = new Jitter('red');
    bug5 = new Jitter('blue');
    bug6 = new Jitter('blue');
    bug7 = new Jitter('blue');
    bug8 = new Jitter('blue');
}

function draw() {
    if (!freeze)
        {
          background(0, 0, 0);
          /* Following lines to be removed (bugs are going to be grouped in an app class)*/
          bug1.move();
          bug1.display();
          bug2.move();
          bug2.display();
          bug3.move();
          bug3.display();
          bug4.move();
          bug4.display();
          bug5.move();
          bug5.display();
          bug6.move();
          bug6.display();
          bug7.move();
          bug7.display();
          bug8.move();
          bug8.display();
        }
    else
        {
            /* Following lines to be removed (bugs are going to be grouped in an app class)*/
            bug1.color = 'grey';
            bug2.color = 'grey';
            bug3.color = 'grey';
            bug4.color = 'grey';
            bug5.color = 'grey';
            bug6.color = 'grey';
            bug7.color = 'grey';
            bug8.color = 'grey';
            bug1.display();
            bug2.display();
            bug3.display();
            bug4.display();
            bug5.display();
            bug6.display();
            bug7.display();
            bug8.display();

        }
}

class App{
    constructor(n_targets, n_distractors, target_color, distractor_color){
        this.n_targets = n_targets;
        this.n_distractors = n_distractors;
        this.targets = [];
        this.distractors = [];
        for(let step = 0; step < this.n_targets; step++){
            this.targets.push(new Jitter('red'))
        }
        for(let step = 0; step < this.n_distractors; step++){
            this.targets.push(new Jitter('blue'))
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

// Jitter class
class Jitter {
  constructor(color) {
    this.x = random(width);
    this.y = random(height);
    this.diameter = random(20, 50);
    this.dir = Math.floor(random(0,7)+1);
    this.x_speed = 3;
    this.y_speed = 3;
    this.color = color;
  }
  move() {
    if (this.x > width) {
        this.x = width ;
        this.x_speed = -1*this.x_speed;
    }
    else if (this.x < 0) {
        this.x = 0;
        this.x_speed = -1*this.x_speed;
    }
    else if (this.y > height) {
        this.y = height;
        this.y_speed = -1*this.y_speed;
    }
    else if (this.y < 0) {
        this.y = 0;
        this.y_speed = -1*this.y_speed;
    }
    else{
        switch (this.dir)
        {
            case 0:
                this.x -=  this.x_speed;
            case 1:
                this.x -=  this.x_speed;
                this.y -= this.y_speed;
            case 2:
                this.y -= this.y_speed;
            case 3:
                this.x +=  this.x_speed;
                this.y -= this.y_speed;
            case 4:
                this.x +=  this.x_speed;
            case 5:
                this.x +=  this.x_speed;
                this.y += this.y_speed;
            case 6:
                this.y += this.y_speed;
            case 7:
                this.y += this.y_speed;
                this.x -=  this.x_speed;
        }
    }
  }
  display() {
      fill(this.color);
      ellipse(this.x, this.y, this.diameter, this.diameter);
  }
}
