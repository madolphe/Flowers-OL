
//p5.js preload images
function preload() {

  //load_imgs(loop_imgs);
  //num_targlist = stats_targ.getRowCount();
  stats_targ = loadTable(fname_target);
  stats_filler = loadTable(fname_filler);
  img_bkg = loadImage(fname_bkg);
  success = loadImage(fname_success);
  console.log('done preload')

}

//p5.js initializing.
function setup() {
  createCanvas(Pos.canvas_width,Pos.canvas_height);

  for (let i=0; i < num_targlist; ++i) {
    Imgs_targ[i] = loadImage(stats_targ.get(i, 0));
    print(stats_targ.get(i, 0))
  }

  for (let i=0; i < num_fillerlist; ++i) {
    Imgs_filler[i] = loadImage(stats_filler.get(i, 0));
    print(stats_filler.get(i, 0))
  }

  create_end_button();
  Params = new ParameterManager(); 
  Time = new TimeManager();
  
  create_next_button();
  create_previous_button();
  create_start_button();
  
  bar = new progressBar(5);
  
  console.log('done setup')
}

//p5.js frame animation.
function draw() {
  //console.log('start draw')
  background(col_bkg); //bkg color
  image(img_bkg,Pos.center_x-(Pos.size_bkg_x/2),0,Pos.size_bkg_x,Pos.size_bkg_y);
  //Main experiment schedule
  Time.show();
}


function load_imgs(callback){
  stats_targ = loadTable('./img/list_img_target.csv');
  stats_filler = loadTable('./img/list_img_filler.csv');
  callback();
}

function loop_imgs(){
  for (let i=0; i < num_targlist; ++i) {
    Imgs_targ[i] = loadImage(stats_targ.get(i, 0));
    print(stats_targ.get(i, 0))
  }

  for (let i=0; i < num_fillerlist; ++i) {
    Imgs_filler[i] = loadImage(stats_filler.get(i, 0));
    print(stats_filler.get(i, 0))
  }
}


function keyPressed(){
  if(keyCode===32){
    fullscreen(true);
  }
}


function getRandomInt(min,max) {
  return (Math.floor(Math.random() * Math.floor(max-min)))+min;
}


