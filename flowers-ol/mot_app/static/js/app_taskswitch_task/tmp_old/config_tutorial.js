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

let flag_practice = true;
let canvas_w = Math.round(12*ppd);
let canvas_h = Math.round(10*ppd);


let num_rep = 2; 
let array_stimcond = [1,1,1,0,0,0]; //this parameter is used for the switching flag. 
let array_taskcond = ['Color','Shape']; //Tasks switch condition.
let array_textleft = ['Red:f','Circle:f'];
let array_textright = ['Blue:j','Square:j']; 
let array_colorcond = [0,1]; //0:color 0, 1:color 1
let array_shapecond = [0,1]; //0:color 0, 1:color 1
let col_0 =[128,0,0];
let col_1 = [0,0,128];

let keyRes1 = 70; //f
let keyRes2 = 74; //j

let time_stimduration = 4000; //in ms
let time_maskduration = 1000; //in ms
let time_isi = 0; //in ms
let time_fixation = 1500; // in millisecond

//object condition
let size_obj = Math.round(2*ppd); //in pix. in diameter


// fixation 
let col_instruction = 255;
let size_instruction = Math.round(0.75*ppd); //in pix

// text 
let col_text = 255;
let size_text = Math.round(0.5*ppd); //in pix
////

let col_bkg = 128;

//
let pos_guide = Math.round(3*ppd);

let x_ok = -Math.round(1.5*ppd);
let y_ok = Math.round(4*ppd);
let x_restart = -Math.round(6*ppd);; //in pixel
let y_restart = -Math.round(5*ppd);; //in pixel