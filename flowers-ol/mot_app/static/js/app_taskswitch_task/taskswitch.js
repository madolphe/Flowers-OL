//p5.js preload images
function preload() {
  //img = loadImage('./img/noise.png');
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
    scene_fixation(scene_isi);
  }else if(Time.scene==2){
    scene_stim();
  }else if(Time.scene==3){
    scene_backmask();
  }else if(Time.scene==4){
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
  } else {
    fill(col_text);
    textSize(size_text);
    textAlign(CENTER);
    text( "Please click the mouse to start this experiment", CANVAS_WIDTH/2, (CANVAS_HEIGHT/2)+(size_text/2));
  }
}

//scene 1
function scene_fixation(callback){
  Time.count();
  if (Time.activetime_block < time_fixation) {
    push();
    fill(col_instruction);
    textSize(size_instruction);
    noStroke();
    textAlign(CENTER);
    text(Params.taskcond[Params.ind_task],CANVAS_WIDTH/2, (CANVAS_HEIGHT/2)+(size_instruction/2));
    pop();

  } else {
    callback();
  }
}


function scene_isi(){
  if (Time.activetime_block < time_fixation + time_isi){
    //show a blank for this experiment
    //image(img, (CANVAS_WIDTH/2)-(size_img[0]/2), (CANVAS_HEIGHT/2)-(size_img[1]/2));
  } else{
    Time.update();
  }
}


//scene 2
function scene_stim(){
  Time.count();
  if (keyIsPressed){
    if (keyCode == keyRes1) {
      Time.count_response();
      Params.tmp_res_ob = 1;
      Time.update();
    } else if (keyCode == keyRes2) {
      Time.count_response();
      Time.tmp_res_ob = 2;
      Time.update();
    }
  }

  if (Time.activetime_block < time_stimduration){    
    push();
    fill(Params.color);
    noStroke();
    if (Params.shapecond[0] ==0){
      rect((CANVAS_WIDTH/2)-(size_obj/2), (CANVAS_HEIGHT/2)-(size_obj/2), size_obj, size_obj);
    }else{
      ellipse(CANVAS_WIDTH/2, CANVAS_HEIGHT/2, size_obj, size_obj);
    }
    pop();
    push();
    fill(col_instruction);
    textSize(size_instruction);
    noStroke();
    textAlign(CENTER);
    text(array_textleft[Params.ind_task],(CANVAS_WIDTH/2)-pos_guide, (CANVAS_HEIGHT/2)+(size_instruction/2));
    text(array_textright[Params.ind_task],(CANVAS_WIDTH/2)+pos_guide, (CANVAS_HEIGHT/2)+(size_instruction/2));
    pop();
    
  } else{
    Time.update();
  }
}




function scene_backmask(){
  Time.count();
  if (Time.activetime_block <  time_maskduration){
    //show a blank for this experiment
    //image(img, (CANVAS_WIDTH/2)-(size_img[0]/2), (CANVAS_HEIGHT/2)-(size_img[1]/2));
  } else{
    Time.update();
  }
}

// scene 3
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
      'results_responses': Params.results_responses,
      'results_rt': Params.results_rt,
      'results_ind_switch': Params.results_ind_switch,
      'results_taskcond': Params.results_taskcond,
      'results_colorcond': Params.results_colorcond,
      'results_shapecond': Params.results_shapecond
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

    this.scene_key = 3;
    this.scene_back = 1;
    this.end_scene = 4;

  }

  update(){
    if(this.scene==this.scene_key){
      //here is the end part of the trial.
      this.repeat();
      this.starttime_block = Date.now();      
    }else{
      this.scene ++;
      this.starttime_block = Date.now();
    }
  }

  repeat(){
    if (Params.flag_block ==true){
      // This experiment is regarded as one block experiment. The preset repetetion is recalculated in one block in the constructer.
      Params.next_block();
      this.scene = this.end_scene;
      if (flag_practice==false){
        button_end.show();
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

////////////////////////////////////////
class ParameterManager{
  constructor() {
    // Stimulus parameters
    this.repetition = 0;
    this.ind_stimcond = 0;
    this.flag_block = false;

    // condition setting
    this.ind_switch = [];
    for (let i=0;i<num_rep;i++){
      this.ind_switch = concat(this.ind_switch,array_stimcond);
    }
    this.ind_switch = shuffle(this.ind_switch);

    this.ind_task = shuffle([0,1]); 
    this.ind_task = int(this.ind_task[0]); //initialize the first task;

    this.taskcond = array_taskcond;
    this.colorcond = shuffle(array_colorcond);
    this.shapecond = shuffle(array_shapecond);
    if (this.colorcond[0]==0){
      this.color = col_0;
    } else{
      this.color = col_1;
    }

    // Results parameters;
    this.tmp_res_ob = 0;
    this.tmp_rt = null;
    this.results_responses = [];
    this.results_rt = [];
    this.results_ind_switch = [];
    this.results_taskcond = [];
    this.results_colorcond = [];
    this.results_shapecond = [];

  }
  
  next_trial(){
    this.save(); //This task saves the data once per block.

    //set the next trial parameters
    this.set_stimlusorder_trial();
    this.ind_stimcond ++;
    this.tmp_res_ob = 0;
    if (this.ind_stimcond==this.ind_switch.length){
      this.flag_block = true;
    }
  }

  next_block(){
    //in this experiment, this function is just for the save of the last trial.
    //The last value of the ind_switch is the same as the one before just for pudding.
    this.ind_stimcond = this.ind_stimcond-1;
    this.save(); 
  }

  set_stimlusorder_trial(){
    console.log(this.ind_switch);
    console.log(this.ind_stimcond)
    console.log(this.ind_task)
    console.log(array_textleft[this.ind_task])
    if (this.ind_switch[this.ind_stimcond]==1){
      this.ind_task = Math.abs(this.ind_task -1);
    }

    this.colorcond = shuffle(array_colorcond);
    this.shapecond = shuffle(array_shapecond);
    if (this.colorcond[0]==0){
      this.color = col_0;
    } else{
      this.color = col_1;
    }
  }


  save(){
    // store the current stimulus and response data to the result dictionary.
    this.results_responses.push(this.tmp_res_ob);
    this.results_rt.push(this.tmp_rt);
    this.results_ind_switch.push(this.ind_switch[this.ind_stimcond]);
    this.results_taskcond.push(this.taskcond[this.ind_task]);
    this.results_colorcond.push(this.colorcond[0]);
    this.results_shapecond.push(this.shapecond[0]);
  }
}

 //To randomize the stimulus condition.
const shuffle = ([...array]) => {
  for (let i = array.length - 1; i >= 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}
