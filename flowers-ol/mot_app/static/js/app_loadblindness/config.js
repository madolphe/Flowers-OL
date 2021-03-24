//// parameters
//let CANVAS_WIDTH = 640;
//let CANVAS_HEIGHT = 480;

let num_rep = 40; 
let array_stimcond = [0,1,2,3]; //Experimental condition. 

let array_fixation = [0,1];
let length_longer = 10; //in pix


let time_stimduration = 100; //in ms
let time_maskduration = 1900; //in ms
let time_fixation = 1000; // in millisecond
let col_target = 255;
let size_target = 200;


//save array. just be stored in the prensetation order.
let array_responses =[];
let array_rt =[];
let array_stimuli =[];
let array_previousstimuli =[];


// fixation 
let len_fixation = 20; // in pix
let col_fixation = [0,0,0]; // in rgb
let thick_fixation = 5; // in pix


// text 
let col_text = 255;
let size_text = 28;
let size_text_button = 24;
let Buttons = [];
////

// image
let size_img = 256;
let contrast_img_correct = 0.8;
let contrast_img_wrong = 0.4;
let distance_from_center =  200; //in pix;

let x_ok = 0;
let y_ok = 200;
