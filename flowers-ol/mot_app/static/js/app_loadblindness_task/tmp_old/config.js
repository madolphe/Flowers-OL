//// parameters

// number of pixels per degres:
let viewer_dist = 50;
// let screen_params = 1920/34.25; // width pixels/cm in sawayama's monitor
let ppcm = screen.availWidth / screen_params
let ppd = get_ppd(viewer_dist, ppcm);

//just for my local debug
function get_ppd(viewer_dist, screen_params){
    return (viewer_dist*Math.tan(Math.PI/180)) * screen_params;
}

let flag_practice = false;

//let num_rep = 20;
let num_rep = 1;

let keyRes1 = 70; //f
let keyRes2 = 74; //j

let array_stimcond = [0,1,2,3]; //Experimental condition.

let array_fixation = [0,1];
let length_longer = Math.round(0.8*ppd); //in pix


let time_stimduration = 100; //in ms
//let time_maskduration = 1900; //in ms
let time_maskduration = 10; //in ms
//let time_fixation = 1000; // in millisecond
let time_fixation = 10; // in millisecond
let col_target = 255;

let col_bkg = 128;

// fixation 
let len_fixation = Math.round(1*ppd); // in pix
let col_fixation = 20; // in rgb
let thick_fixation = Math.round(0.1*ppd); // in pix


// text 
let col_text = 255;
let size_text = Math.round(1*ppd); //in pix
let size_text_button = 24;
let Buttons = [];
////

// image
let size_img = Math.round(3.6*ppd); //in pix
let contrast_img_correct = 0.9;
let contrast_img_wrong = 0.3;
let ind_distance = [0,1];
let distance_from_center =  [Math.round(3*ppd),Math.round(6*ppd)]; //in pix;

let x_ok = -Math.round(0*ppd);
let y_ok = Math.round(4*ppd);
let x_restart = -Math.round(5.5*ppd);; //in pixel
let y_restart = -Math.round(4*ppd);; //in pixel

let pos_guide = Math.round(2*ppd);
