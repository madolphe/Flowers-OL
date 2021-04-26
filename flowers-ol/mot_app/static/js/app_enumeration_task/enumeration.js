//p5.js preload images
function preload() {
  img = loadImage(fname_noise);
  img_bkg = loadImage(fname_bkg);
  success = loadImage(fname_success);
}

//p5.js initializing.
function setup() {
  //createCanvas(CANVAS_WIDTH,CANVAS_HEIGHT);
  createCanvas(Pos.canvas_width,Pos.canvas_height);
  Params = new ParameterManager();
  Time = new TimeManager();
  create_answer_button();
  create_selector_input();
  create_end_button();
  
  create_next_button();
  create_previous_button();
  create_start_button();

  bar = new progressBar(5);
}

//p5.js frame animation.
function draw() {
  background(col_bkg); //bkgground color
  //game body
  image(img_bkg,Pos.center_x-(Pos.size_bkg_x/2),0,Pos.size_bkg_x,Pos.size_bkg_y);

  //Main experiment schedule
  Time.show();  
}

///Settings for screen mode and buttons. 

function windowResized() {
  resizeCanvas(Pos.canvas_width,Pos.canvas_height);
}

function keyPressed(){
  if(keyCode===32){
    fullscreen(true);
  }
}


//////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////
//To do:complete this function and replace this with image loading.

function make_whitenoise(image,size_img = 800){
  let noise_1d = make_array(0,256-1,256);
  noise_1d= shuffle(noise_1d);
  for (let y=0;y<size_img;y++){
    for (let x=0;x<size_img;x++){
      image.set(y,x,[noise_1d[0],noise_1d[0],noise_1d[0],255]);
    }
  }
  image.updatePixels();
}