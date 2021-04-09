//// parameters

// number of pixels per degres:
let viewer_dist = 50;
let screen_params = 1920/34.25; // width pixels/cm in sawayama's monitor
let ppd = get_ppd(viewer_dist, screen_params);

function get_ppd(viewer_dist, screen_params){
    return (viewer_dist*Math.tan(Math.PI/180)) * screen_params;
}

let flag_practice = false;

let keyRes1 = 70; //f
let keyRes2 = 74; //j

let num_rep = 50; 
let array_stimcond = [1,2,3,4,5,6,7,8,9]; //Experimental condition. 
let stim_target = 3;
let stim_filler = [1,2,4,5,6,8,9];
let stim_previous = 7;


let time_stimduration = 50; //in ms Mani et al., (2005)
let time_maskduration = 950; //in ms
let col_target = 255;
let size_target = Math.round(1.5*ppd); //in pix 

let col_bkg = 128;

// fixation 
let len_fixation = Math.round(1*ppd); // in pix
let col_fixation = 20; // in rgb
let thick_fixation = Math.round(0.1*ppd); // in pix
let time_fixation = 1000; // in millisecond

// text 
let col_text = 255;
let size_text = Math.round(1*ppd); //in pixel
////

let x_ok = -Math.round(0*ppd);
let y_ok = Math.round(4*ppd);
let x_restart = -Math.round(5.5*ppd);; //in pixel
let y_restart = -Math.round(4*ppd);; //in pixel

let col_0 =[128,0,0];
let col_1 = [0,0,128];