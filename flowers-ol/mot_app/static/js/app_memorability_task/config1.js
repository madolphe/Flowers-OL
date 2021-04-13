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
let prac_num_rep = 30; //ignored in the main exp.

let fname_target = './img/list_img_target1.csv';
let fname_filler = './img/list_img_filler1.csv';

let keyRes1 = 70; //f
let keyRes2 = 74; //j

let num_rep = 1; 

//number of lists
let num_stimulus = 120;
let num_targlist = 25;
let num_fillerlist = 70;

//Stimulus condition.
let num_longtarget =  5;
let dict_longtarget = [0,1,2,3,4,5,6,7,8,9];
let distance_longtarget = [100,101,102,103,104,105,106,107,108,109];

let num_shorttarget = 20;
let min_shorttarget = 1;
let max_shorttarget = 92;
let distance_shorttarget = [3,4,5,6,3,4,5,6,3,4,5,6,3,4,5,6,3,4,5,6];

let ind_targlist = make_array(0,num_targlist-1,num_targlist); 
let ind_fillerlist = make_array(0,num_fillerlist-1,num_fillerlist); 


let time_stimduration = 1000; //in ms
let time_fixation = 1400; // in millisecond
let time_feedback = 1400; // in millisecond

let col_bkg = 128;

// fixation 
let len_fixation = Math.round(1*ppd); // in pix
let col_fixation = [20,20,20]; // in rgb
let thick_fixation = Math.round(0.1*ppd); // in pix

// text 
let col_text = 255;
let size_text = Math.round(1*ppd); //in pix
////

let Imgs_targ = [];
let Imgs_filler = [];
let size_img = 700; 
let size_rescale = Math.round(6.5*ppd); //in pix


//feedback params
let col_correct = [0,0,128];
let size_correct = Math.round(1*ppd); //in pix
let col_wrong = [128,0,0];
let size_wrong = Math.round(1*ppd);  //in pix

let x_ok = -Math.round(0*ppd);
let y_ok = Math.round(4*ppd);
let x_restart = -Math.round(5.5*ppd);; //in pixel
let y_restart = -Math.round(4*ppd);; //in pixel

// window size control.
let scale_window = 0.8;

let pos_guide = Math.round(6*ppd); //in pix

function make_array(val_start, val_stop, num_array) {
    let array = [];
    let step = (val_stop - val_start) / (num_array - 1);
    for (let i = 0; i < num_array; i++) {
      array.push(val_start + (step * i));
    }
    return array;
  }
  