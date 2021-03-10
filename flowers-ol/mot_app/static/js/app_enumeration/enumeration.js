//We will conduct this experiment by a method of constant, one of the psychophysical methodologes.

//p5.js preload images
function preload() {
  img = loadImage('/static/images/enumeration_imgs/noise.png');
}

//p5.js initializing.
function setup() {
  createCanvas(displayWidth, displayHeight);
  Time = new TimeManager();
  CANVAS_WIDTH = displayWidth;
  CANVAS_HEIGHT = displayHeight;
}

//p5.js frame animation.
function draw() {
  background(128); //bkg color
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

//scene 0
function scene_instruction(){
  if (mouseIsPressed) {
    Time.update();
  } else {
    fill(col_text);
    textSize(size_text);
    textAlign(CENTER);
    text( "Please press the space key to start this experiment", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
  }
}
function keyPressed(){
  if(keyCode===32){
    fullscreen(true);
  }
}

//scene 1
function scene_fixation(){
  Time.count();
  if (Time.activetime_block < duration_fixation) {
    stroke(col_fixation); // define gray scale color (0 to 255) of lines
    strokeWeight(thick_fixation);
    line(CANVAS_WIDTH/2 - len_fixation, CANVAS_HEIGHT/2, CANVAS_WIDTH/2 + len_fixation, CANVAS_HEIGHT/2 );
    line(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - len_fixation, CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + len_fixation );
  } else {
    Time.update();
  }
}


//scene 2
function show_stim(){
  Time.count();
  if (Time.activetime_block < time_stimduration){
    for (let i=0; i < Time.trial_numobj[Time.ind_numobj]; ++i) {
      Objs[i].display();
    }
  } else{
    Time.update();
  }
}

function scene_stim(callback){
  if (f_load==false){
    Objs = [];
    for (let i=0; i < Time.trial_numobj[Time.ind_numobj]; ++i) {
      Objs.push(make_pos(Objs))
    };
    Time.blockstart();
    f_load = true; 
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
  text( "How many circles are presented?", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
}

function make_button(){
  sel = createSelect();
  sel.position(x_response+CANVAS_WIDTH/2, y_response+CANVAS_HEIGHT/2);    

  for (i=0; i < max_answer; i++) {
    sel.option(`${i+1}`);
  }
  sel.changed(active_button);
}


function active_button(){
  let item = sel.value();
  button_ok = createButton('OK');
  button_ok.position(x_ok+CANVAS_WIDTH/2, y_ok+CANVAS_HEIGHT/2);
  button_ok.mousePressed(()=>{
    //save the response and the stimulus condition
    array_responses.push(item);
    array_stimuli.push(Time.trial_numobj[Time.ind_numobj])
    button_ok.hide();
    sel.hide();
    Time.update();    
    });
}

// scene 5
function scene_end(){
  if (mouseIsPressed) {
    Time.update();
  } else {
    fill(col_text);
    textSize(size_text);
    textAlign(CENTER);
    text( "Thank you for joining the experiment.", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
  }
}


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

class TimeManager{
  constructor() {
    this.scene = 0;
    this.starttime_exp = Date.now();
    this.starttime_block = null;
    this.activetime_block = null;
    this.repetition = -1;
    this.ind_numobj = array_numobj.length-1;
    this.trial_numobj = null;
  }

  update(){
    if(this.scene===0){
      // called from the instruction scene
      this.scene ++;
      this.starttime_block = Date.now();
      this.repeat();
    }else if(this.scene===1){
      // called from the fixation scene
      this.ind_numobj ++;
      this.scene ++;
      f_load = false;
      this.starttime_block = Date.now();
    }else if(this.scene===2){
      // called from the stimuli scene
      this.scene ++;
      this.starttime_block = Date.now();
    }else if(this.scene===3){
      // called from the stimuli scene
      this.scene ++;
      this.starttime_block = Date.now();
      make_button();
    }else if(this.scene===4){
      // called from the response scene
      this.repeat();
      this.starttime_block = Date.now();
    }
  }

  repeat(){
    if (this.ind_numobj==array_numobj.length-1){
      this.trial_numobj = shuffle(array_numobj);
      this.ind_numobj = -1;
      this.repetition ++;
      if (this.repetition == num_rep){
        this.scene = 5;
      }else{
        this.scene = 1;
      }
    }else{
      this.scene = 1;
    }
  }
  count(){
    // Calculate the duration since the target scene (block) started
    this.activetime_block = (Date.now() - this.starttime_block);
  }

  blockstart(){
    // Just to increase the stimulus duration accuracy when you present the experimental stimuli.
    this.starttime_block = Date.now();
  }
 }

 //To randomize the stimulus condition.
// I may don't need this
const shuffle = ([...array]) => {
  for (let i = array.length - 1; i >= 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

