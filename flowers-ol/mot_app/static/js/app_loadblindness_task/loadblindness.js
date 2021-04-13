//p5.js preload images
function preload() {
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

  img_correct = createImage(size_img, size_img);
  console.log(round(size_img));
  img_correct.loadPixels();
  make_gabor_correct(img_correct,contrast_img_correct,size_img=size_img,sigma=round(size_img/5));
  
  img_wrong = createImage(size_img, size_img);
  img_wrong.loadPixels();
  make_gabor_wrong(img_wrong,contrast_img_wrong,size_img=size_img,sigma=round(size_img/5));

  create_answer_button();
  create_end_button();
  if (flag_practice==true){
    create_restart_button();
  }else{
    create_end_button();
  }
}

//p5.js frame animation.
function draw() {
  background(col_bkg); //bkg color
  //Main experiment schedule

  if(Time.scene==0){
    scene_instruction();
  }else if(Time.scene==1){
    scene_fixation();
  }else if(Time.scene==2){
    scene_stim(scene_targ);
  }else if(Time.scene==3){
    scene_key_response();
  }else if(Time.scene==4){
    scene_response();
  }else if(Time.scene==5){
    scene_end();
  }
}

function keyPressed(){
  if(keyCode===32){
    fullscreen(true);
  }
}


//scene 0
function scene_instruction(){
  if (mouseIsPressed) {
    Time.update();
  } else{
    fill(col_text);
    textSize(size_text);
    textAlign(CENTER);
    text( "Please click the mouse to start this experiment", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
  }
}

//scene 1
function scene_fixation(){
  Time.count();
  if (Time.activetime_block < time_fixation) {
    push();
    fill(col_fixation);
    ellipse(CANVAS_WIDTH/2, CANVAS_HEIGHT/2,len_fixation,len_fixation);
    pop();
  } else{
    Time.update();
  }
}


//scene 2
function scene_targ(){
  if (Time.activetime_block < time_stimduration + time_maskduration){
  } else{
    Time.update();
  }
}


function scene_stim(callback){
  Time.count();

  if (Time.activetime_block < time_stimduration){   
    push();
    for (let i=0;i<4;i++){
      if (i==0){
        image(img_correct,Params.dict_pos[Params.trial_stimcond[i]][0],Params.dict_pos[Params.trial_stimcond[i]][1])
      } else{
        image(img_wrong,Params.dict_pos[Params.trial_stimcond[i]][0],Params.dict_pos[Params.trial_stimcond[i]][1])
      }     
    }
    stroke(col_fixation); // define gray scale color (0 to 255) of lines
    strokeWeight(thick_fixation);
    line(CANVAS_WIDTH/2 - len_fixation - Params.dict_fixation[Params.trial_fixation[0]][0], CANVAS_HEIGHT/2, CANVAS_WIDTH/2 + len_fixation+Params.dict_fixation[Params.trial_fixation[0]][0], CANVAS_HEIGHT/2);
    line(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - len_fixation-Params.dict_fixation[Params.trial_fixation[0]][1], CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + len_fixation+Params.dict_fixation[Params.trial_fixation[0]][1]);
    pop();

  } else{
    callback();
  }
}

// scene 3
function scene_key_response(){
  Time.count();
  if (keyIsPressed){
    if (keyCode == keyRes1) {
      Time.count_response();
      Params.tmp_res_fixation = 0;
      Time.update();
    } else if (keyCode == keyRes2) {
      Time.count_response();
      Params.tmp_res_fixation = 1;
      Time.update();
    }
  }
  push();
  fill(col_text);
  textSize(size_text);
  textAlign(CENTER);
  text( 'Which line was longer, vertical or horizontal?', CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
  text( 'Vertical:press key "f"     Horizontal:press key"j"', CANVAS_WIDTH/2, (CANVAS_HEIGHT/2)+pos_guide);
  pop();
}

// scene 4
function scene_response(){
  Time.count();
  push();
  fill(col_text);
  textSize(size_text);
  textAlign(CENTER);
  text( 'Which target contrast was strong?', CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
  pop();

  for (let i=0;i<4;i++){
    if (i==0) {
      Buttons[i].mousePressed(fnc_correct);
    }else{
      Buttons[i].mousePressed(fnc_false);
    }
  }
}

function create_answer_button(){
  for (let i=0;i<4;i++){
    Buttons[i] = createButton("Here!"); 
    Buttons[i].size(size_img, size_img);
    Buttons[i].style('font-size', size_text_button + 'px');
    Buttons[i].position(Params.dict_pos[Params.trial_stimcond[i]][0],Params.dict_pos[Params.trial_stimcond[i]][1])
    Buttons[i].hide();
  }
}

function make_button(){
  for (let i=0;i<4;i++){
    Buttons[i].show(); 
    Buttons[i].position(Params.dict_pos[Params.trial_stimcond[i]][0],Params.dict_pos[Params.trial_stimcond[i]][1])
  }  
}

function fnc_correct(){
  Time.count_response();
  Params.tmp_res_ob = 1;
  for (let i=0;i<4;i++){
      Buttons[i].hide();
  }
  Time.update();
}

function fnc_false(){
  Time.count_response();
  Params.tmp_res_ob = 0;
  for (let i=0;i<4;i++){
      Buttons[i].hide();
  }
  Time.update();
}

// scene 5
function scene_end(){
  fill(col_text);
  noStroke();
  textSize(size_text);
  textAlign(CENTER);
  text( "Thank you for joining the experiment.", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
}

function create_end_button(){
  button_end = createButton('END');
  button_end.position(x_ok+CANVAS_WIDTH/2, y_ok+CANVAS_HEIGHT/2);
  button_end.mousePressed(quit_task);
  button_end.hide();
}

function quit_task(){
  fullscreen(false);
  let parameters_to_save = {
      'results_responses_pos': Params.results_responses_pos,
      'results_responses_fix': Params.results_responses_fix,
      'results_rt': Params.results_rt,
      'results_targetvalue_stim': Params.results_targetvalue_stim,
      'results_targetvalue_fixation': Params.results_targetvalue_fixation,
      'results_target_distance': Params.results_target_distance
    }
  post('exit_view_cognitive_task', parameters_to_save, 'post');
}

function create_restart_button(){
  button_restart = createButton('RESTART');
  //button_restart.position(x_ok+CANVAS_WIDTH/2, y_ok+CANVAS_HEIGHT/2);
  button_restart.position(x_restart+CANVAS_WIDTH/2, y_restart+CANVAS_HEIGHT/2);
  button_restart.mousePressed(restart_task);
}

function restart_task(){
  Params = new ParameterManager();
  Time = new TimeManager();
}


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

 class ParameterManager{
  constructor() {
    // Stimulus parameters
    this.repetition = 0;
    this.ind_stimcond = 0;
    this.flag_block = false;
    this.repetition = 0;

    //ConditionManager
    this.trial_ind_distance = shuffle(ind_distance);
    this.x_pos1 = (CANVAS_WIDTH/2)-distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2))-size_img;
    this.x_pos2 = (CANVAS_WIDTH/2)+distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2));
    this.y_pos1 = (CANVAS_HEIGHT/2)-distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2))-size_img;
    this.y_pos2 = (CANVAS_HEIGHT/2)+distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2));
    this.dict_pos = [[this.x_pos1,this.y_pos1],[this.x_pos2,this.y_pos1],[this.x_pos1,this.y_pos2],[this.x_pos2,this.y_pos2]];
    this.dict_fixation = [[0,length_longer],[length_longer,0]];

    this.trial_fixation = shuffle(array_fixation);
    this.trial_stimcond = shuffle(array_stimcond); 
    this.tmp_res_ob = 0;
    this.tmp_res_fixation = null;

    //save
    this.results_responses_pos = [];
    this.results_responses_fix = [];
    this.results_rt = [];
    this.results_targetvalue_stim = [];
    this.results_targetvalue_fixation = [];
    this.results_target_distance = []

  }
  
  next_trial(){
    //if not correct response for fixation length, the process doesn't go on.
    if (this.tmp_res_fixation==this.trial_fixation[0]){
    this.save(); 
    //set the next trial parameters
    this.trial_fixation = shuffle(array_fixation);
    this.trial_stimcond = shuffle(array_stimcond); 
    this.ind_stimcond ++;
    this.tmp_res_ob = 0;
    this.tmp_res_fixation = null;
    this.x_pos1 = (CANVAS_WIDTH/2)-distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2))-size_img;
    this.x_pos2 = (CANVAS_WIDTH/2)+distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2));
    this.y_pos1 = (CANVAS_HEIGHT/2)-distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2))-size_img;
    this.y_pos2 = (CANVAS_HEIGHT/2)+distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2));
    this.dict_pos = [[this.x_pos1,this.y_pos1],[this.x_pos2,this.y_pos1],[this.x_pos1,this.y_pos2],[this.x_pos2,this.y_pos2]];
    if (this.ind_stimcond==ind_distance.length-1){
      this.flag_block = true;
    }
    }
    this.trial_fixation = shuffle(array_fixation);
    this.trial_stimcond = shuffle(array_stimcond);
  }

  //no block at the moment in this experiment
  next_block(){
    if (this.tmp_res_fixation==this.trial_fixation[0]){
    //set the next block parameters
    this.save(); 
    this.repetition ++;
    this.trial_ind_distance = shuffle(ind_distance);
    this.ind_stimcond = 0;
    this.flag_block = false;
    this.tmp_res_ob = 0;
    this.tmp_res_fixation = null;
    this.x_pos1 = (CANVAS_WIDTH/2)-distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2))-size_img;
    this.x_pos2 = (CANVAS_WIDTH/2)+distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2));
    this.y_pos1 = (CANVAS_HEIGHT/2)-distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2))-size_img;
    this.y_pos2 = (CANVAS_HEIGHT/2)+distance_from_center[this.trial_ind_distance[this.ind_stimcond]]*(1/Math.sqrt(2));
    this.dict_pos = [[this.x_pos1,this.y_pos1],[this.x_pos2,this.y_pos1],[this.x_pos1,this.y_pos2],[this.x_pos2,this.y_pos2]];
    }
    this.trial_fixation = shuffle(array_fixation);
    this.trial_stimcond = shuffle(array_stimcond); 
  }

  save(){
    // save the current result.
    this.results_responses_pos.push(this.tmp_res_ob);
    this.results_responses_fix.push(this.tmp_res_fixation);
    this.results_rt.push(this.tmp_rt);
    this.results_targetvalue_stim.push(this.trial_stimcond[this.ind_stimcond]);
    this.results_targetvalue_fixation.push(this.trial_fixation[0]);
    this.results_target_distance.push(distance_from_center[this.trial_ind_distance[this.ind_stimcond]]);
    //console.log('response is');
    //console.log(this.tmp_res_ob);
  }


}

///////////////////////////////////////////////////////////

//draw gabor 後でクラス継承をして整える
function make_gabor_correct(image_correct,contrast=1,size_img = 256,sigma=50,freq=8,theta=90,phase=0){
  let theta_rad = deg2rad(theta);
  let phase_rad = deg2rad(phase);
    
  let x_1d = make_array(-0.5,0.5,size_img);
  sigma_norm = sigma/size_img;

  for (let y=0;y<x_1d.length;y++){
    for (let x=0;x<x_1d.length;x++){
      let val_tmp = Math.sin((((x_1d[x]*Math.cos(theta_rad))+(x_1d[y]*Math.sin(theta_rad))) * freq * 2 * Math.PI)+phase_rad)*
                      Math.exp(-(((x_1d[x]**2)+(x_1d[y]**2))/(2* (sigma_norm**2))));
      val_tmp = contrast*val_tmp;
      val_tmp = 255*((val_tmp+1)/2)
      image_correct.set(y,x,[val_tmp,val_tmp,val_tmp,255]);
    }
  }
  image_correct.updatePixels();
}

function make_gabor_wrong(image_wrong,contrast=1,size_img = 256,sigma=50,freq=8,theta=90,phase=0){
  let theta_rad = deg2rad(theta);
  let phase_rad = deg2rad(phase);
    
  let x_1d = make_array(-0.5,0.5,size_img);
  sigma_norm = sigma/size_img;

  for (let y=0;y<x_1d.length;y++){
    for (let x=0;x<x_1d.length;x++){
      let val_tmp = Math.sin((((x_1d[x]*Math.cos(theta_rad))+(x_1d[y]*Math.sin(theta_rad))) * freq * 2 * Math.PI)+phase_rad)*
                      Math.exp(-(((x_1d[x]**2)+(x_1d[y]**2))/(2* (sigma_norm**2))));
      val_tmp = contrast*val_tmp;
      val_tmp = 255*((val_tmp+1)/2)
      image_wrong.set(y,x,[val_tmp,val_tmp,val_tmp,255]);
    }
  }
  image_wrong.updatePixels();
}


function make_array(val_start, val_stop, num_array) {
  let array = [];
  let step = (val_stop - val_start) / (num_array - 1);
  for (let i = 0; i < num_array; i++) {
    array.push(val_start + (step * i));
  }
  return array;
}
  
function deg2rad(degrees) {
  let pi = Math.PI;
  return degrees * (pi/180);
}
  


//To randomize the stimulus condition.
const shuffle = ([...array]) => {
  for (let i = array.length - 1; i >= 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}



