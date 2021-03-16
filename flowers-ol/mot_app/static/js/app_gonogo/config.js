//// parameters

//const CANVAS_WIDTH = 640;
//const CANVAS_HEIGHT = 480;

let num_rep = 50; 
let array_stimcond = [1,2,3,4,5,6,7,8,9]; //Experimental condition. 
let stim_target = 3;
let stim_filler = [1,2,4,6,7,8,9];
let stim_previous = 5;


let time_stimduration = 500; //in ms
let time_maskduration = 700; //in ms
let col_target = 255;
let size_target = 200;


//save array. just be stored in the prensetation order.
let array_responses =[];
let array_rt =[];
let array_stimuli =[];
let array_previousstimuli =[];


// fixation 
let len_fixation = 20; // in pix
let col_fixation = 20; // in rgb
let thick_fixation = 5; // in pix
let time_fixation = 1000; // in millisecond

// text 
let col_text = 255;
let size_text = 28;
////

let x_ok = 0;
let y_ok = 200;
