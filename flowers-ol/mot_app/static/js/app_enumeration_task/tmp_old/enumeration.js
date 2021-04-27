let bar, success, div_ticks;
//p5.js preload images
function preload() {
  img = loadImage('/static/images/pre-post-imgs/noise.png');
  success = loadImage('static/images/icons/success.png'); ///here
}
//p5.js initializing.
function setup() {
  if (flag_practice==true){
  CANVAS_WIDTH = canvas_w;
  CANVAS_HEIGHT = canvas_h;
  }else{
  CANVAS_WIDTH = displayWidth;
  CANVAS_HEIGHT = displayHeight;    
  }
  createCanvas(CANVAS_WIDTH,CANVAS_HEIGHT);
  Params = new ParameterManager();
  Time = new TimeManager();
  create_answer_button();
  create_selector_input();

  if (flag_practice==true){
    create_restart_button();
  }else{
    create_end_button();
  }
  bar = new progressBar(5); ///here
}

//p5.js frame animation.
function draw() {
  background(col_bkg); //bkg color
  //Main experiment schedule
  bar.draw();
  if(Time.scene==0){
    scene_instruction();
  }else if(Time.scene==1){
    scene_fixation();
  }else if(Time.scene==2){
    scene_stim(show_stim);
  }else if(Time.scene==3){
    scene_backmask();
  }else if(Time.scene==4){
    scene_response();
  }else if(Time.scene==5){
    scene_end();
  }
}

function keyPressed(){
  if(keyCode===32 && !flag_practice){
    fullscreen(true);
  }
}

//scene 0
function scene_instruction(){
  if (mouseIsPressed) {
    Time.update();
  } else {
    fill(col_text);
    textSize(size_text);
    textAlign(CENTER);
    text( prompt_start, CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
  }
}

//scene 1
function scene_fixation(){
  Time.count();
  if (Time.activetime_block < time_fixation) {
    push();
    stroke(col_fixation); // define gray scale color (0 to 255) of lines
    strokeWeight(thick_fixation);
    line(CANVAS_WIDTH/2 - len_fixation, CANVAS_HEIGHT/2, CANVAS_WIDTH/2 + len_fixation, CANVAS_HEIGHT/2 );
    line(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - len_fixation, CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + len_fixation );
    pop();
  } else {
    Time.update();
  }
}


//scene 2
function show_stim(){
  Time.count();
  if (Time.activetime_block < time_stimduration){
    for (let i=0; i < Params.trial_stimcond[Params.ind_stimcond]; ++i) {
      Objs[i].display();
    }
  } else{
    Time.update();
  }
}

function scene_stim(callback){
  if (Params.flag_load==false){
    Objs = [];
    for (let i=0; i < Params.trial_stimcond[Params.ind_stimcond]; ++i) {
      Objs.push(make_pos(Objs))
    };
    Time.blockstart();
    Params.flag_load = true; 
  }else{
    callback();
  }
}

//make object class not overlapping with other positions.
function make_pos(Objs){
  let Obj = [];
  let flag_overlap = false;
  while (Obj.length < 1){
    let x = int((CANVAS_WIDTH/2)-(roi_obj/2)) + int(random(roi_obj));
    let y = int((CANVAS_HEIGHT/2)-(roi_obj/2)) + int(random(roi_obj));
    for (j=0;j < Objs.length; j++){
      flag_overlap = false;
      let d = dist(x,y,Objs[j].x,Objs[j].y);
      if (d < Objs[j].diameter){
        flag_overlap = true;
        break;
      }
    }
    if (flag_overlap == false){
      Obj = new DrawEllipse(size_obj,x,y)
    }
  }
  return Obj
}


// scene 3
function scene_backmask(){
  Time.count();
  if (Time.activetime_block < time_maskduration){
    image(img, (CANVAS_WIDTH/2)-(size_img[0]/2), (CANVAS_HEIGHT/2)-(size_img[1]/2));
  } else{
    Time.update();
  }
}


// scene 4
function scene_response(){  
  fill(col_text);
  textSize(size_text);
  textAlign(CENTER);
  text( prompt_question, CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
}

// functions to run only when loading page:
function create_selector_input(){
  sel = createSelect();
  sel.position(x_response+CANVAS_WIDTH/2, y_response+CANVAS_HEIGHT/2);
  sel.id('input_select');
  div_ticks = createDiv('ticks');

  for (i=0; i < max_answer; i++) {
    sel.option(`${i+1}`);
    var tmp_span = createSpan(`${i+1}`);
    tmp_span.addClass('tick');
    tmp_span.parent(div_ticks);
  }

  sel.changed(active_button);
  sel.hide();
}
function create_answer_button(){
  button_ok = createButton('OK');
  button_ok.position(x_ok+CANVAS_WIDTH/2, y_ok+CANVAS_HEIGHT/2);
  button_ok.hide();
}
// Make inputs visible for user:
function make_button(){
  sel.show();
  button_ok.show();
}
function active_button(){
  let item = sel.value();
  button_ok.mousePressed(()=>{
    //save the response and the stimulus condition
    Params.tmp_res_ob = item;
    button_ok.hide();
    sel.hide();
    Time.update();    
    });
}

// scene 5
function scene_end(){
  fill(col_text);
  noStroke();
  textSize(size_text);
  textAlign(CENTER);
  text( prompt_gratitude, CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
}

function create_end_button(){
  button_end = createButton('END');
  button_end.position(x_ok+CANVAS_WIDTH/2, y_ok+CANVAS_HEIGHT/2);
  button_end.mousePressed(quit_task);
  button_end.hide();
}


function quit_task(){
  fullscreen(false);
  //here
  let parameters_to_save = {
      'results_responses': Params.results_responses,
      'results_rt': Params.results_rt,
      'results_targetvalue': Params.results_targetvalue
    }
  post('exit_view_cognitive_task', parameters_to_save, 'post');
}


function create_restart_button(){
  button_restart = createButton(prompt_button_restart);
  //button_restart.position(x_ok+CANVAS_WIDTH/2, y_ok+CANVAS_HEIGHT/2);
  button_restart.position(x_restart+CANVAS_WIDTH/2, y_restart+CANVAS_HEIGHT/2);
  button_restart.mousePressed(restart_task);
}

function restart_task(){
  Params = new ParameterManager();
  Time = new TimeManager();
}

//////////////////////////////////////////////////////////////

class DrawEllipse {
  constructor(diameter,x,y) {
    noStroke();
    this.diameter = diameter;
    this.x = x;
    this.y = y;
  }

  display() {
    ellipse(this.x, this.y, this.diameter, this.diameter);
  }
 }

//////////////////////////////////////////////////////////////

 class TimeManager{
  constructor() {
    this.scene = 0;
    this.starttime_exp = Date.now();
    this.starttime_block = null;
    this.activetime_block = null;

    this.scene_key1 = 4;
    this.scene_key2 = 3;
    this.scene_back = 1;
    this.end_scene = 5;
  
  }

  update(){
    if(this.scene==this.scene_key1){
      //here is the end part of the trial.
      this.repeat();
      this.starttime_block = Date.now();      
    }else if (this.scene==this.scene_key2) {
      this.scene ++;
      make_button();
      this.starttime_block = Date.now();
    }else{
      this.scene ++;
      this.starttime_block = Date.now();
    }
  }

  repeat(){
    if (Params.flag_block ==true){
      Params.next_block();
      if (Params.repetition == num_rep){
        this.scene = this.end_scene;
        if (flag_practice==false){
          button_end.show();
        }        
      }else{
        this.scene = this.scene_back;
      }
    }else{
      Params.next_trial();      
      this.scene = this.scene_back;
    }
  }
  count(){
    // Calculate the duration since the target scene (block) started
    this.activetime_block = (Date.now() - this.starttime_block);
  }

  count_response(){
    // Calculate the reaction time of the participant
    Params.tmp_rt = (Date.now() - this.starttime_block);
  }

  blockstart(){
    this.starttime_block = Date.now();
  }
}

//////////////////////////////////////////////////////////////

class ParameterManager{
  constructor() {
    // Stimulus parameters
    this.repetition = 0;
    this.ind_stimcond = 0;
    this.flag_block = false;
    this.trial_stimcond = shuffle(array_stimcond);
    this.flag_load = false;

    this.tmp_res_ob = 0;
    this.tmp_rt = 0;
    this.results_responses = [];
    this.results_rt = [];
    this.results_targetvalue = [];
  }

  next_trial(){
    this.save(); 
    //set the next trial parameters
    this.flag_load = false;
    this.ind_stimcond ++;
    this.tmp_res_ob = 0;
    if (this.ind_stimcond==array_stimcond.length-1){
      this.flag_block = true;
    }
  }

  next_block(){
    this.save(); 
    //set the next block parameters
    this.flag_load = false;
    this.repetition ++;
    this.trial_stimcond = shuffle(array_stimcond);
    this.ind_stimcond = 0;
    this.flag_block = false;
    this.tmp_res_ob = 0;
  }

  save(){
    // save the current result.
    this.results_responses.push(this.tmp_res_ob);
    this.results_rt.push(this.tmp_rt);
    this.results_targetvalue.push(this.trial_stimcond[this.ind_stimcond]);
    //console.log('response is');
    //console.log(this.tmp_res_ob);
  }

}

//////////////////////////////////////////////////////////////

 //To randomize the stimulus condition.
const shuffle = ([...array]) => {
  for (let i = array.length - 1; i >= 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}


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

