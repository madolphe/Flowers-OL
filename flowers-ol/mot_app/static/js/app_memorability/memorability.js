
//p5.js preload images
function preload() {

  //load_imgs(loop_imgs);
  //num_targlist = stats_targ.getRowCount();
  stats_targ = loadTable(fname_target);
  stats_filler = loadTable(fname_filler);
  console.log('done preload')

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
  if (flag_practice==true){
    create_restart_button();
  }else{
    create_end_button();
  }
  console.log('done setup')
  
}

//p5.js frame animation.
function draw() {
  //console.log('start draw')
  background(col_bkg); //bkg color
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
    if(keyCode===keyRes1) {
      Time.count_response();
      Params.tmp_res_ob = 1;
    }
  }

  if (Time.activetime_block < time_stimduration){    
    push();
    //image(Imgs[0],CANVAS_WIDTH,CANVAS_HEIGHT);    
    
    if (Params.array_stim[Params.ind_stimcond]==0){
      Imgs_filler[Params.trial_stimind[Params.ind_trial_filler]].resize(size_rescale, size_rescale);
      image(Imgs_filler[Params.trial_stimind[Params.ind_trial_filler]],(CANVAS_WIDTH/2)-(size_rescale/2),(CANVAS_HEIGHT/2)-(size_rescale/2));
    }else if (Params.array_stim[Params.ind_stimcond]==1){
      Imgs_targ[Params.ind_trial_target1].resize(size_rescale, size_rescale);
      image(Imgs_targ[Params.ind_trial_target1],(CANVAS_WIDTH/2)-(size_rescale/2),(CANVAS_HEIGHT/2)-(size_rescale/2));
    }else if (Params.array_stim[Params.ind_stimcond]==2){
      Imgs_targ[Params.ind_trial_target2].resize(size_rescale, size_rescale);
      image(Imgs_targ[Params.ind_trial_target2],(CANVAS_WIDTH/2)-(size_rescale/2),(CANVAS_HEIGHT/2)-(size_rescale/2));
    }
    
    /*
    pop();
    push();
    fill(col_text);
    textSize(size_text);
    textAlign(CENTER);
    text( 'Press key "f" if you saw this previously', CANVAS_WIDTH/2, (CANVAS_HEIGHT/2)+pos_guide);
    pop();
    */
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
      'results_targetvalue': Params.results_targetvalue,
      'results_flagcorrect':Params.results_flagcorrect,
      'results_ind_trial_filler':Params.results_ind_trial_filler,
      'results_ind_trial_target1':Params.results_ind_trial_target1,
      'results_ind_trial_target2':Params.results_ind_trial_target2
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
      Params.make_responseflag();
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

    this.flag_correct = true;


    ind_targlist = shuffle(ind_targlist);
    ind_fillerlist = shuffle(ind_fillerlist);

    dict_longtarget = shuffle(dict_longtarget);
    distance_shorttarget = shuffle(distance_shorttarget);

    this.array_stim = Array(num_stimulus).fill(0)
    this.trial_stimind = [];

    this.ind_trial_filler = 0
    this.ind_trial_target1 = 0
    this.ind_trial_target2 = 0

    
    
    let j = 0;
    while (j < num_longtarget){
      let tmp1 = this.array_stim[dict_longtarget[j]] + 1;
      distance_longtarget = shuffle(distance_longtarget);
      let tmp2 = this.array_stim[dict_longtarget[j]+distance_longtarget[0]]+1;
      if (tmp1==1 && tmp2==1){
        this.array_stim[dict_longtarget[j]] = 1
        this.array_stim[dict_longtarget[j]+distance_longtarget[0]] = 2
        j = j+1;
      }
    }
    
    
    j = 0;
    while (j < num_shorttarget){
      let ind_tmp = getRandomInt(min_shorttarget,max_shorttarget)
      let tmp1 = this.array_stim[ind_tmp] + 1;
      let tmp2 = this.array_stim[ind_tmp+distance_shorttarget[j]]+1;
      if (tmp1==1 && tmp2==1){
        this.array_stim[ind_tmp] = 1;
        this.array_stim[ind_tmp+distance_shorttarget[j]] = 2;
        j = j+1;
      }
    }

    console.log('ok until here2')

    let k = 0;
    let l = 0;
    let m = 0;
    for (let i=0;i<num_stimulus;i++){
      if (this.array_stim[i]==0){
        this.trial_stimind.push(ind_fillerlist[k]);
        k ++;
      }else if (this.array_stim[i]==1){
        //console.log(l)
        this.trial_stimind.push(ind_targlist[l]);
        l ++;
      } else if (this.array_stim[i]==2){
        //console.log(m)
        this.trial_stimind.push(ind_targlist[m]);
        m ++;
      }
    }

    // Results parameters;
    this.tmp_res_ob = 0;
    this.tmp_rt = null;
    this.results_responses = [];
    this.results_rt = [];
    this.results_targetvalue = [];
    this.results_flagcorrect = [];
    this.results_ind_trial_filler = [];
    this.results_ind_trial_target1 = [];
    this.results_ind_trial_target2 = [];
  }


  next_trial(){
    this.save();

    //set the next trial parameters
    if (this.array_stim[this.ind_stimcond]==0){
      this.ind_trial_filler ++;
    }else if (this.array_stim[this.ind_stimcond]==1){
      this.ind_trial_target1 ++;
    } else if (this.array_stim[this.ind_stimcond]==2){
      this.ind_trial_target2 ++;
    }

    this.ind_stimcond ++;
    this.tmp_res_ob = 0;
    
    if (flag_practice==true){
      if (this.ind_stimcond==prac_num_rep-1){
        this.flag_block = true;
        button_end.show();
      }
    } else{
      if (this.ind_stimcond==num_stimulus-1){
        this.flag_block = true;
        button_end.show();
      }
    }
  }

  next_block(){
    this.save();
    //assuming only one block

    //set the next block parameters
    this.repetition ++;
    this.ind_stimcond = 0;
    this.flag_block = false;
    this.tmp_res_ob = 0;
  }

  make_responseflag(){
    if (this.array_stim[this.ind_stimcond]==2){
      if (this.tmp_res_ob==1){
        this.flag_correct = true;
      }else{
        this.flag_correct = false;
      }
    } else{
      if (this.tmp_res_ob==1){
        this.flag_correct = false;
      }else{
        this.flag_correct = true;
      }
    }
  }

  save(){
    // save the current result.
    this.results_responses.push(this.tmp_res_ob);
    this.results_rt.push(this.tmp_rt);
    this.results_targetvalue.push(this.array_stim[this.ind_stimcond]);
    this.results_flagcorrect.push(this.flag_correct)

    //set the next trial parameters
    if (this.array_stim[this.ind_stimcond]==0){
      this.results_ind_trial_filler.push(this.ind_trial_filler);
    }else if (this.array_stim[this.ind_stimcond]==1){
      this.results_ind_trial_target1.push(this.ind_trial_target1);
    } else if (this.array_stim[this.ind_stimcond]==2){
      this.results_ind_trial_target2.push(this.ind_trial_target2);
    }

    //console.log('response is');
    //console.log(this.tmp_res_ob);
  }
}


function getRandomInt(min,max) {
  return (Math.floor(Math.random() * Math.floor(max-min)))+min;
}


//To randomize the stimulus condition.
const shuffle = ([...array]) => {
  for (let i = array.length - 1; i >= 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}
