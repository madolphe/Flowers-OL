//// parameters

//const CANVAS_WIDTH = 640;
//const CANVAS_HEIGHT = 480;

let num_rep = 30; 
let array_stimcond = [1,1,1,0,0,0];
let array_taskcond = ['Color','Shape']; //Tasks switch condition.
let array_colorcond = [0,1]; //0:color 0, 1:color 1
let array_shapecond = [0,1]; //0:color 0, 1:color 1
let col_0 =[128,0,0];
let col_1 = [0,0,128];

let time_stimduration = 2000; //in ms
let time_maskduration = 1000; //in ms
let time_isi = 200; //in ms
let time_fixation = 700; // in millisecond

//object condition
let size_obj = 200; //in pix. in diameter

//save array. just be stored in the prensetation order.
let array_responses =[];
let array_rt =[];
let array_task =[];
let array_color =[];
let array_shape =[];


// fixation 
let col_instruction = 255;
let size_instruction = 100;

// text 
let col_text = 255;
let size_text = 28;
////


let x_ok = 0;
let y_ok = 200;
