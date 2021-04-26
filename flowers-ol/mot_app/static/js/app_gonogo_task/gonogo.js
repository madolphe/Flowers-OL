//p5.js preload images
function preload() {
  img_bkg = loadImage(fname_bkg);
  success = loadImage(fname_success);
}

//p5.js initializing.
function setup() {
  createCanvas(Pos.canvas_width,Pos.canvas_height);
  Params = new ParameterManager(); 
  Time = new TimeManager();

  create_end_button();

  create_next_button();
  create_previous_button();
  create_start_button();

  bar = new progressBar(5);
}

//p5.js frame animation.
function draw() {
  background(col_bkg); //bkg color
  image(img_bkg,Pos.center_x-(Pos.size_bkg_x/2),0,Pos.size_bkg_x,Pos.size_bkg_y);
  //Main experiment schedule

  Time.show();
}

function keyPressed(){
  if(keyCode===32){
    fullscreen(true);
  }
}

