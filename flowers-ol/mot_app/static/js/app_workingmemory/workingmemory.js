//p5.js preload images
function preload() {
}

//p5.js initializing.
function setup() {
  createCanvas(displayWidth, displayHeight);
  CANVAS_WIDTH = displayWidth;
  CANVAS_HEIGHT = displayHeight;
  CENTER_X = (CANVAS_WIDTH/2)-(size_target/2);
  CENTER_Y = (CANVAS_HEIGHT/2)-(size_target/2); 
  Params = new ParameterManager();
  Time = new TimeManager();

  create_answer_button();
  create_end_button();
}

//p5.js frame animation.
function draw() {
  background(128); //bkg color
  //Main experiment schedule

  if(Time.scene==0){
    scene_instruction();
  }else if(Time.scene==1){
    scene_fixation();
  }else if(Time.scene==2){
    scene_stim(scene_targ);
  }else if(Time.scene==3){
    scene_response();
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
    stroke(col_fixation); 
    strokeWeight(thick_fixation);
    line(CANVAS_WIDTH/2 - len_fixation, CANVAS_HEIGHT/2, CANVAS_WIDTH/2 + len_fixation, CANVAS_HEIGHT/2 );
    line(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - len_fixation, CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + len_fixation );
    pop();
  } else{
    Time.update();
  }
}


//scene 2
function scene_targ(){
  Time.count();
  if (Time.activetime_block < time_stimduration){
    
    for (let i=0; i < array_stimcond.length; ++i) {
      if (i==Params.count_color && i<num_memory){
        push();
        fill(col_target);
        Objs[i].display();
        pop();
      }else{
        push();
        fill(col_normal);
        Objs[i].display();
        pop();
      }
    }

  } else{
    Time.update();
  }

  if (Time.activetime_block > time_startblank+((Params.count_color+1)*time_onestimduration)){
    Params.count_color ++;
  }
}


function scene_stim(callback){
  if (Params.flag_load == false){   
    for (let i=0; i < array_stimcond.length; ++i) {
      Objs[i] = new DrawRect(size_target,Params.dict_pos[Params.trial_stimcond[i]][0],Params.dict_pos[Params.trial_stimcond[i]][1])
    };
  Time.blockstart();
  Params.flag_load = true;
  } else{
    callback();
  }
}

class DrawRect {
  constructor(size,x,y) {
    noStroke();
    this.size = size;
    this.x = x
    this.y = y
  }

  display() {
    rect(this.x, this.y, this.size, this.size);
  }
 }

// scene 4
function scene_response(){
  Time.count();
  // call function
  for (let i=0; i < array_stimcond.length; ++i) {
    Button[i].mousePressed(record_response);
  }

  if (Params.tmp_res_ob.length==num_memory){
    Time.update();
  }
}

function create_answer_button(){
  for (let i=0; i < array_stimcond.length; ++i) {
    Button[i] = createButton("Click in order");
    Button[i].style('font-size', size_text_button + 'px');
    Button[i].size(size_target, size_target);
    Button[i].position(Params.dict_pos[Params.trial_stimcond[i]][0],Params.dict_pos[Params.trial_stimcond[i]][1]);
    Button[i].hide();
  }
}

function make_button(){
  for (let i=0; i < array_stimcond.length; ++i){
    Button[i].show(); 
    Button[i].position(Params.dict_pos[Params.trial_stimcond[i]][0],Params.dict_pos[Params.trial_stimcond[i]][1]);
  }  
}


function record_response(){
  Params.order++;
  Params.tmp_res_ob.push(Params.order);
}

// scene 5
function scene_end(){
  if (mouseIsPressed) {
    Time.update();
  } else {
    fill(col_text);
    noStroke();
    textSize(size_text);
    textAlign(CENTER);
    text( "Thank you for joining the experiment.", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
  }
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
      'results_targetvalue_stim': Params.results_targetvalue_stim
    }
  post('cognitive_assessment_home', parameters_to_save, 'post');
}

class TimeManager{
  constructor() {
    this.scene = 0;
    this.starttime_exp = Date.now();
    this.starttime_block = null;
    this.activetime_block = null;

    this.scene_key1 = 3;
    this.scene_key2 = 2;
    this.scene_back = 1;
    this.end_scene = 4;
  }

  update(){
    if(this.scene==this.scene_key1){
      for (let i=0; i < array_stimcond.length; ++i) {
        Button[i].hide();
      }
      this.repeat();
      this.starttime_block = Date.now();      
    }else if (this.scene==this.scene_key2) {
      make_button();
      this.scene ++;
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
        button_end.show();
      }else{
        this.scene = this.scene_back;
      }
    }else{
      //In this experiment, no trial.
      //this.Params.next_trial(); 
      //this.scene = this.scene_back;
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
    this.flag_block = true; //no trial
    this.flag_load = false;
    this.count_color = -1;   
    //ConditionManager
    
    this.dict_pos = [[CENTER_X-shift_position,CENTER_Y-shift_position],
                      [CENTER_X,CENTER_Y-shift_position],
                      [CENTER_X+shift_position,CENTER_Y-shift_position],
                      [CENTER_X-shift_position,CENTER_Y],
                      [CENTER_X,CENTER_Y],
                      [CENTER_X+shift_position,CENTER_Y],
                      [CENTER_X-shift_position,CENTER_Y+shift_position],
                      [CENTER_X,CENTER_Y+shift_position],
                      [CENTER_X+shift_position,CENTER_Y+shift_position],];

    this.trial_stimcond = shuffle(array_stimcond); 
    this.tmp_res_ob = [];
    this.order = -1;

    //save
    this.results_responses = [];
    this.results_rt = [];
    this.results_targetvalue_stim = [];

  }
    next_trial(){
      //set the next trial parameters 
      this.ind_stimcond ++;
      if (this.ind_stimcond==num_memory-1){
        this.flag_block = true;
      }
    }
  
    next_block(){
      this.save(); 
      //set the next block parameters

      this.count_color = -1;
      this.flag_load = false;
      this.repetition ++;
      this.trial_stimcond = shuffle(array_stimcond); 
      this.ind_stimcond = 0;
      this.tmp_res_ob = [];
      this.order = -1;
    }
  
    save(){
      // save the current result.
      this.results_responses.push(this.tmp_res_ob);
      this.results_rt.push(this.tmp_rt);
      this.results_targetvalue_stim.push(this.trial_stimcond);
      //console.log('response is');
      //console.log(this.tmp_res_ob);
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

