//// parameters

// number of pixels per degres:
let viewer_dist = 50;
let screen_params = 1920/34.25; // width pixels/cm in sawayama's monitor
let ppd = get_ppd(viewer_dist, screen_params);

//just for my local debug
function get_ppd(viewer_dist, screen_params){
    return (viewer_dist*Math.tan(Math.PI/180)) * screen_params;
}

//const CANVAS_WIDTH = 640;
//const CANVAS_HEIGHT = 480;

let num_rep = 20; // the experiment is conducted by psudo randomizing (common in psychological exps).
let num_memory = [4,5,6,7]; //Experimental condition.
let array_stimcond = [0,1,2,3,4,5,6,7,8]; 


let time_onestimduration = 300; //in ms
let time_stimduration = 3000; //in ms
let time_startblank = 300;
let time_fixation = 1000; // in millisecond
let size_target = 200;

let Objs = [];
let col_normal = [255,255,255];
let col_target = [128,0,0];


// fixation 
let len_fixation = 1*ppd; // in pix
let col_fixation = 20; // in rgb
let thick_fixation = 0.1*ppd; // in pix


// text 
let col_text = 255;
let size_text = 1*ppd; //in pix
let size_text_button = 1*ppd; //in pix
////

let shift_position = 5*ppd; //in pix

let Button = [];
let x_ok = 0;
let y_ok = 200;
