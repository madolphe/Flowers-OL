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

let num_rep = 10; 
let array_stimcond = [1,1,1,0,0,0];
let array_taskcond = ['Color','Shape']; //Tasks switch condition.
let array_textleft = ['Red:f','Circle:f'];
let array_textright = ['Blue:j','Square:j']; 
let array_colorcond = [0,1]; //0:color 0, 1:color 1
let array_shapecond = [0,1]; //0:color 0, 1:color 1
let col_0 =[128,0,0];
let col_1 = [0,0,128];

let keyRes1 = 70; //f
let keyRes2 = 74; //j

let time_stimduration = 2000; //in ms
let time_maskduration = 1000; //in ms
let time_isi = 0; //in ms
let time_fixation = 650; // in millisecond

//object condition
let size_obj = Math.round(2*ppd); //in pix. in diameter


// fixation 
let col_instruction = 255;
let size_instruction = Math.round(1*ppd); //in pix

// text 
let col_text = 255;
let size_text = Math.round(1*ppd); //in pix
////


let x_ok = 0;
let y_ok = 200;

//
let pos_guide = Math.round(5*ppd);
