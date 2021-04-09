//// parameters

// number of pixels per degres:
let viewer_dist = 50;
let screen_params = 1920/34.25; // width pixels/cm in sawayama's monitor
let ppd = get_ppd(viewer_dist, screen_params);

//just for my local debug
function get_ppd(viewer_dist, screen_params){
    return (viewer_dist*Math.tan(Math.PI/180)) * screen_params;
}

let flag_practice = true;
let canvas_w = Math.round(12*ppd);
let canvas_h = Math.round(10*ppd);

let num_rep = 3; // the experiment is conducted by psudo randomizing (common in psychological exps).
let num_memory = [3,4]; //Experimental condition.
let array_stimcond = [0,1,2,3,4,5,6,7,8]; 


let time_onestimduration = 1000; //in ms
let time_stimduration = 5000; //in ms
let time_startblank = 500;
let time_fixation = 1000; // in millisecond
let size_target = Math.round(2*ppd); //in pixel

let Objs = [];
let col_normal = [255,255,255];
let col_target = [128,0,0];

let col_bkg = 128;

// fixation 
let len_fixation = 0.5*ppd; // in pix
let col_fixation = 20; // in rgb
let thick_fixation = 0.1*ppd; // in pix


// text 
let col_text = 255;
let size_text = 0.5*ppd; //in pix
let size_text_button = 0.5*ppd; //in pix
////

let shift_position = 3*ppd; //in pix

let Button = [];

let x_ok = -Math.round(1.5*ppd);
let y_ok = Math.round(4*ppd);
let x_restart = -Math.round(6*ppd);; //in pixel
let y_restart = -Math.round(5*ppd);; //in pixel