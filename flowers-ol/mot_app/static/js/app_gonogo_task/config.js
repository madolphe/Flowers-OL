//// parameters

//////////////////////////Monitor 
// number of pixels per degres:
let viewer_dist = 50;
function get_ppd(viewer_dist, screen_params){
    return (viewer_dist*Math.tan(Math.PI/180)) * screen_params;
}
let window_availw = window.screen.availWidth;
let window_availh = window.screen.availHeight;

//let window_availw = window.screen.width;
//let window_availh = window.screen.height;

let size_screen_cm_w = 34.25; // width pixels/cm in sawayama's monitor
//let screen_params = 1920/34.25; // width pixels/cm in sawayama's monitor
let screen_params = window_availw/size_screen_cm_w;
let ppd = get_ppd(viewer_dist, screen_params);
//////////////////////////Monitor 

let fname_bkg = '../img/bkg_finger1.png';
let size_bkg_width_orig = 1440; //original in pix
let size_bkg_height_orig = 1080; //original in pix
let ratio_center = 0.1111; 
let ratio_monitor = 0.706;
Pos = new PositionManager(window_availw,window_availh);
Pos.adjust_to_bkg(size_bkg_width_orig,size_bkg_height_orig,ratio_center);
let img_bkg;

let flag_practice = true;
let flag_break = true;
let count_break = 0;
let max_break = 5;

let num_rep_main = 10; 
let num_rep_practice = 2;

let time_stimduration_main = 50; //in ms Mani et al., (2005)
let time_stimduration_practice = 1000; //in ms Mani et al., (2005)

let array_stimcond = [1,2,3,4,5,6,7,8,9]; //Experimental condition. 
let stim_target = 3;
let stim_filler = [1,2,4,5,6,8,9];
let stim_previous = 7;

let keyRes1 = 74; //j
//let keyRes2 = 70; //f

let time_maskduration = 950; //in ms
let col_target = 255;
let size_target = Math.round(1.5*ppd); //in pix 

let col_bkg = 0;

// fixation 
let len_fixation = Math.round(0.5*ppd); // in pix
let col_fixation = 20; // in rgb
let thick_fixation = Math.round(0.1*ppd); // in pix
let time_fixation = 1000; // in millisecond

// text 
let col_text = 255;
let size_text = Math.round(0.7*ppd); //in pixel
////

let x_ok = -Math.round(0*ppd);
let y_ok = Math.round(4*ppd);
let x_restart = -Math.round(5.5*ppd);; //in pixel
let y_restart = -Math.round(4*ppd);; //in pixel

let col_0 =[128,0,0];
let col_1 = [0,0,128];

let text_start = "Please click the mouse to start this experiment";
let text_end = "Thank you for joining the experiment.";