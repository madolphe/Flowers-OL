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
    push();
    fill(col_text);
    textSize(size_text);
    textAlign(CENTER);
    text( "Please click the mouse to start this experiment", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
    pop();
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
function scene_targ(){
  if (Time.activetime_block < time_stimduration + time_maskduration){ 
    if (Params.ind_stimcond==Params.ind_previous+1){
      if (flag_practice==true){
        Params.feedback();
      }
    }
  } else{
    Time.update();
  }
}

function scene_stim(callback){
  Time.count();

  if (Params.ind_stimcond==Params.ind_previous+1){
    if (keyIsPressed){
      // 32 means space
      if (keyCode == keyRes1) {
        if (Params.flag_gonogo[Params.repetition]==1){
          Time.count_response();
          Params.tmp_res_ob = 1; //1 means the correct response.
        }else{
          Time.count_response();
          Params.tmp_res_ob = 2; //2 means the false alarm.
        }
      }
    }
  }


  if (Time.activetime_block < time_stimduration){    
    push();
    fill(col_target);
    textSize(size_target);
    noStroke();
    textAlign(CENTER);
    text("%d".replace("%d",Params.trial_stimcond[Params.ind_stimcond]), CANVAS_WIDTH/2, (CANVAS_HEIGHT/2)+(size_target/2));;
    pop();
  } else{
    callback();
  }
}

// scene 4
function scene_end(){
    push();
    fill(col_text);
    noStroke();
    textSize(size_text);
    textAlign(CENTER);
    text( "Thank you for joining the experiment.", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
    pop();
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
      'results_ind_previous': Params.results_ind_previous,
      'results_targetvalue': Params.results_targetvalue
    }
  post('cognitive_assessment_home', parameters_to_save, 'post');
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

    this.scene_key = 2;
    this.scene_back = 2;
    this.end_scene = 3;

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
    this.previous_buffer = null;
    this.flag_block = false;

    // go nogo setting
    this.trial_stimcond = shuffle(array_stimcond);
    this.stim_target = stim_target;
    this.stim_previous = stim_previous;
    this.stim_filler = shuffle(stim_filler);
    this.ind_previous = null;
    this.ind_targ = null;

    let num_true = round(num_rep/2)
    this.flag_gonogo = Array.prototype.concat(
      new Array(num_true).fill(1),
      new Array(num_rep-num_true).fill(0));
    this.flag_gonogo = shuffle(this.flag_gonogo);
    this.set_stimlusorder();

    // Results parameters;
    this.tmp_res_ob = 0;
    this.tmp_rt = null;
    this.results_responses = [];
    this.results_rt = [];
    this.results_ind_previous = [];
    this.results_targetvalue = [];
  }
  
  next_trial(){
    if (this.ind_stimcond==this.ind_previous+1){
      this.save(); //This task saves the data once per block.
    } 
    //set the next trial parameters
    this.previous_buffer = this.trial_stimcond[this.ind_stimcond];
    this.ind_stimcond ++;
    this.tmp_res_ob = 0;
    if (this.ind_stimcond==array_stimcond.length-1){
      this.flag_block = true;
    }
  }

  feedback(){
    //still not used
    push();
    noStroke();
    textSize(size_text);
    textAlign(CENTER);
    if(this.trial_stimcond[this.ind_previous+1]==stim_target){
      if (this.tmp_res_ob==1){
        fill(col_1);
        text( "Correct Answer", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
      }else{
        fill(col_0);
        text( "Wrong Answer", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
      }
    }else{
      if (this.tmp_res_ob==2){
        fill(col_0);
        text( "Wrong Answer", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
      }else{
        fill(col_1);
        text( "Correct Answer", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
      }   
    }
    pop();
  }

  next_block(){
    //set the next block parameters
    this.previous_buffer = this.trial_stimcond[this.ind_stimcond];
    this.repetition ++;
    this.set_stimlusorder();
    this.ind_stimcond = 0;
    this.flag_block = false;
    this.tmp_res_ob = 0;
  }

  set_stimlusorder(){
    this.trial_stimcond = shuffle(array_stimcond);
    this.stim_filler = shuffle(stim_filler);
    this.ind_previous = this.trial_stimcond.indexOf(this.stim_previous);
    this.ind_targ = this.trial_stimcond.indexOf(this.stim_target);

    if (this.ind_previous==this.trial_stimcond.length-1){
      let tmp_ind = this.trial_stimcond.indexOf(this.stim_filler[1]);
      this.trial_stimcond[this.ind_previous] = this.stim_filler[1];
      this.trial_stimcond[tmp_ind] = this.stim_previous;
      this.ind_previous = tmp_ind;
    }

    //console.log('gonogo flag is');
    //console.log(this.flag_gonogo[this.repetition]);
    if (this.flag_gonogo[this.repetition]==1){
      if (this.ind_previous+1!=this.ind_targ){
        this.trial_stimcond[this.ind_previous+1] = this.stim_target;
      }
    }else{
      if (this.ind_previous+1==this.ind_targ){
        this.trial_stimcond[this.ind_targ] = this.stim_filler[0];
      }
    }
  }

  save(){
    // save the current result.
    this.results_responses.push(this.tmp_res_ob);
    this.results_rt.push(this.tmp_rt);
    this.results_ind_previous.push(this.ind_previous);
    this.results_targetvalue.push(this.trial_stimcond[this.ind_previous+1]);
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



