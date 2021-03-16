//// parameters

//const CANVAS_WIDTH = 640;
//const CANVAS_HEIGHT = 480;

let num_rep = 1; 
let num_stimulus = 10;
let time_stimduration = 1000; //in ms
let time_fixation = 1400; // in millisecond
let time_feedback = 1400; // in millisecond

let col_target = 255;
let size_target = 200;


//save array. just be stored in the prensetation order.
let array_responses =[];
let array_rt =[];
let array_stimuli =[];
let array_previousstimuli =[];


// fixation 
let len_fixation = 20; // in pix
let col_fixation = [20,20,20]; // in rgb
let thick_fixation = 5; // in pix

// text 
let col_text = 255;
let size_text = 28;
////

let Imgs_targ = [];
let Imgs_filler = [];
let size_img = 1000;
let size_rescale = 256;


//feedback params
let col_correct = [0,0,128];
let size_correct = 32;
let col_wrong = [128,0,0];
let size_wrong = 32;

let x_ok = 0;
let y_ok = 200;
