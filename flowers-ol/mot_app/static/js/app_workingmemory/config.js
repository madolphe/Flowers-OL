//// parameters
//const CANVAS_WIDTH = 640;
//const CANVAS_HEIGHT = 480;

let num_rep = 40; // the experiment is conducted by psudo randomizing (common in psychological exps).
let num_memory = 6; //Experimental condition.
let array_stimcond = [0,1,2,3,4,5,6,7,8]; 
let array_fixation = [0,1];
let length_longer = 6; //in pix


let time_onestimduration = 300; //in ms
let time_stimduration = 3000; //in ms
let time_startblank = 300;
let time_fixation = 1000; // in millisecond
let size_target = 200;

let Objs = [];
let col_normal = [255,255,255];
let col_target = [128,0,0];


//save array. just be stored in the prensetation order.
let array_responses = [];
let array_rt =[];
let array_stimuli =[];

// fixation 
let len_fixation = 20; // in pix
let col_fixation = (255,0,0); // in rgb
let thick_fixation = 5; // in pix


// text 
let col_text = 255;
let size_text = 28;
let size_text_button = 24;
////

let shift_position = 300;

let Button = [];
let x_ok = 0;
let y_ok = 200;
