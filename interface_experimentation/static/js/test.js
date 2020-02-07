let bug1; // Declare objects
let bug2;
let bug3;
let bug4;

function setup() {
  createCanvas(710, 400);
  // Create object
  bug1 = new Jitter();
  bug2 = new Jitter();
  bug3 = new Jitter();
  bug4 = new Jitter();
  bug5 = new Jitter();
  bug6 = new Jitter();
  bug7 = new Jitter();
  bug8 = new Jitter();

}

function draw() {
  background(50, 89, 100);
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
}

// Jitter class
class Jitter {
  constructor() {
    this.x = random(width);
    this.y = random(height);
    this.diameter = random(20, 50);
    this.dir = Math.floor(random(0,7)+1);
    this.x_speed = 3;
    this.y_speed = 3;
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
    ellipse(this.x, this.y, this.diameter, this.diameter);
  }
}
