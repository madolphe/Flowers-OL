
//p5.js preload images
function preload() {
  stats_targ = loadTable('./img/list_img_target.csv');
  stats_filler = loadTable('./img/list_img_filler.csv');
  
}

//p5.js initializing.
function setup() {
  createCanvas(displayWidth, displayHeight);
  CANVAS_WIDTH = displayWidth;
  CANVAS_HEIGHT = displayHeight;
  num_targlist = stats_targ.getRowCount();
  for (let i=0; i < num_targlist; ++i) {
    Imgs_targ[i] = loadImage(stats_targ.get(i, 0));
  }

  num_fillerlist = stats_filler.getRowCount();
  for (let i=0; i < num_fillerlist; ++i) {
    Imgs_filler[i] = loadImage(stats_filler.get(i, 0));
  }

  Params = new ParameterManager(); 
  Time = new TimeManager();
  //pg = createGraphics(size_rescale, size_rescale);
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
    scene_stim();
  }else if(Time.scene==3){
    scene_feedback();
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
    text( "Please click the mouse to start this experiment", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
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
function scene_stim(){
  Time.count();

  if (keyIsPressed){
    if (key == 'space') {
      Time.count_response();
      Params.tmp_res_ob = 1;
    }
  }

  if (Time.activetime_block < time_stimduration){    
    push();
    //image(Imgs[0],CANVAS_WIDTH,CANVAS_HEIGHT);    
    
    if (Params.array_stim[Params.ind_stimcond]==0){
      Imgs_filler[Params.trial_stimind[Params.ind_stimcond]].resize(size_rescale, size_rescale);
      image(Imgs_filler[Params.trial_stimind[Params.ind_stimcond]],(CANVAS_WIDTH/2)-(size_rescale/2),(CANVAS_HEIGHT/2)-(size_rescale/2));
    }else if (Params.array_stim[Params.ind_stimcond]==1){
      Imgs_targ[Params.trial_stimind[Params.ind_stimcond]].resize(size_rescale, size_rescale);
      image(Imgs_targ[Params.trial_stimind[Params.ind_stimcond]],(CANVAS_WIDTH/2)-(size_rescale/2),(CANVAS_HEIGHT/2)-(size_rescale/2));
    }
    
    pop();
  } else{
    Time.update();
  }
}


//scene 3
function scene_feedback(){
  Time.count();
  if (Time.activetime_block < time_feedback) {
    if (Params.flag_correct ==true) {
      push();
      fill(col_correct);
      textSize(size_correct);
      noStroke();
      textAlign(CENTER);
      text('Correct Answer',CANVAS_WIDTH/2, (CANVAS_HEIGHT/2)+(size_correct/2));    
      pop();
    } else {
      push();
      fill(col_wrong);
      textSize(size_wrong);
      noStroke();
      textAlign(CENTER);
      text('Wrong Answer',CANVAS_WIDTH/2, (CANVAS_HEIGHT/2)+(size_wrong/2));    
      pop();
    }
  } else {
    Time.update();
  }
}

// scene 4
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
      'results_targetvalue': Params.results_targetvalue
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
    this.scene_back = 2;
    this.end_scene = 4;
  
  }

  update(){
    if(this.scene==this.scene_key1){
      //here is the end part of the trial.
      this.repeat();
      this.starttime_block = Date.now();      
    }else if (this.scene==this.scene_key2) {
      this.scene ++;
      Params.make_reponseflag();
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

    this.flag_correct = true;

    //Stimulus condition.
    
    let num_longtarget =  3;
    let dict_longtarget = [0,1,2,3,4,5,6,7,8,9];
    let distance_longtarget = [100,101,102,103,104,105,106,107,108,109];

    let num_shorttarget = 15;
    let min_shorttarget = 10;
    let max_shorttarget = 92;
    let distance_shorttarget = [3,4,5,6,7,3,4,5,6,7,3,4,5,6,7];

    let ind_targlist = make_array(0,num_targlist-1,num_targlist); 
    let ind_fillerlist = make_array(0,num_fillerlist-1,num_fillerlist); 

    ind_targlist = shuffle(ind_targlist);
    ind_fillerlist = shuffle(ind_fillerlist);

    let num_target = num_longtarget + num_shorttarget;

    dict_longtarget = shuffle(dict_longtarget);
    distance_shorttarget = shuffle(distance_shorttarget);

    this.array_stim = Array(num_stimulus).fill(0)
    this.trial_stimind = [];

    let j = 0;
    while (j < num_longtarget){
      let tmp1 = this.array_stim[dict_longtarget[j]] + 1;
      distance_longtarget = shuffle(distance_longtarget);
      let tmp2 = this.array_stim[dict_longtarget[j+distance_longtarget]]+1;
      if (tmp1==1 && tmp2==1){
        this.array_stim[dict_longtarget[j]] = 2
        this.array_stim[dict_longtarget[j+distance_longtarget]] = 1
        j = j+1;
      }
    }

    j = 0;
    while (j < num_shorttarget){
      let ind_tmp = getRandomInt(min_shorttarget,max_shorttarget)
      let tmp1 = this.array_stim[ind_tmp] + 1;
      let tmp2 = this.array_stim[ind_tmp+distance_shorttarget[j]]+1;
      if (tmp1==1 && tmp2==1){
        this.array_stim[ind_tmp] = 2;
        this.array_stim[ind_tmp+distance_shorttarget[j]] = 1;
        j = j+1;
      }
    }

    let k = 0;
    let t = 0;
    for (let i=0;i<num_stimulus;i++){
      if (this.array_stim[i]==0){
        this.trial_stimind.push(ind_fillerlist[k]);
        k ++;
      }else if (this.array_stim[i]==1){
        this.trial_stimind.push(ind_targlist[t]);
        t ++;
      }
    }

    // Results parameters;
    this.tmp_res_ob = 0;
    this.tmp_rt = null;
    this.results_responses = [];
    this.results_rt = [];
    this.results_targetvalue = [];
  }


  next_trial(){
    this.save();
    //set the next trial parameters
    this.ind_stimcond ++;
    this.tmp_res_ob = 0;
    if (this.ind_stimcond==num_stimulus-1){
      this.flag_block = true;
    }
  }

  next_block(){
    this.save();

    //set the next block parameters
    this.repetition ++;
    this.ind_stimcond = 0;
    this.flag_block = false;
    this.tmp_res_ob = 0;
  }

  make_responseflag(){
    if (this.array_stim[this.ind_stimcond]==this.tmp_res_ob){
      this.flag_correct = true;
    }else{
      this.flag_correct = false;
    }
  }

  save(){
    // save the current result.
    this.results_responses.push(this.tmp_res_ob);
    this.results_rt.push(this.tmp_rt);
    this.results_targetvalue.push(this.ind_stimcond);
    //console.log('response is');
    //console.log(this.tmp_res_ob);
  }
}


function getRandomInt(min,max) {
  return (Math.floor(Math.random() * Math.floor(max-min)))+min;
}


function make_array(val_start, val_stop, num_array) {
  let array = [];
  let step = (val_stop - val_start) / (num_array - 1);
  for (let i = 0; i < num_array; i++) {
    array.push(val_start + (step * i));
  }
  return array;
}

//To randomize the stimulus condition.
const shuffle = ([...array]) => {
  for (let i = array.length - 1; i >= 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}
