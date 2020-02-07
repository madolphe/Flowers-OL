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
}

// Jitter class
class Jitter {
  constructor() {
    this.x = random(width);
    this.y = random(height);
    this.diameter = random(10, 30);
    this.dir = Math.floor(random(-4,4)+1);
    console.log(width)
    console.log(height)

  }
  move() {
    switch (this.dir) {
        case 1:
            this.x +=1;
        case 2:
            this.x +=1;
            this.y +=1;
        case 3:
            this.y += 1;
        case 4:
            this.x -=1;
            this.y +=1;
        case 5:
            this.x -= 1;
        case 6:
            this.x -=1;
            this.y -=1;
        case 7:
            this.y -=1;
        case 8:
            this.y -=1;
            this.x += 1;
    }
    if (this.x>width || this.x <0 || this.y>height || this.y<0){
        this.dir = Math.floor(random(1,8)+1);
    }
  }

  display() {
    ellipse(this.x, this.y, this.diameter, this.diameter);
  }
}
