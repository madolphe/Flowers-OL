//// parameters

//const CANVAS_WIDTH = 640;
//const CANVAS_HEIGHT = 480;

let num_rep = 1; // the experiment is conducted by psudo randomizing (common in psychological exps).
let array_numobj = [5,6,7,8,9,10,11]; //Experimental condition.
let time_stimduration = 50; //in ms
let time_maskduration = 1000; //in ms

// number of pixels per degres:
let viewer_dist = 50;
let ppd = get_ppd(viewer_dist, screen_params);

//object condition
//let size_obj = 40; //in pix. in diameter
let size_obj = ppd*2; //in pix. in diameter
//let roi_obj = 500; //in pix. in diameter. Later, these value will be determined from the visual angle.
let roi_obj = ppd*9; //in pix. in diameter. Later, these value will be determined from the visual angle.

let Objs = [];
let f_load =false;

//save array. just be stored in the presentation order.
let array_responses =[];
let array_stimuli =[];


// for the mask image
let img;
let size_img = [1024,1024];

// fixation
let len_fixation = 20; // in pix
let col_fixation = 20; // in rgb
let thick_fixation = 5; // in pix
let duration_fixation = 1000; // in millisecond

// text
let col_text = 255;
let size_text = 28;


//button
let sel;
let x_response = 50;
let y_response = 200;
let max_answer = 15;
let x_ok = -50;
let y_ok = 200;
////