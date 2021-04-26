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

let fname_bkg = '../img/bkg_finger2.png';
let size_bkg_width_orig = 1440; //original in pix
let size_bkg_height_orig = 1080; //original in pix
let ratio_center = 0.1111; 
let ratio_monitor = 0.706;
Pos = new PositionManager(window_availw,window_availh);
Pos.adjust_to_bkg(size_bkg_width_orig,size_bkg_height_orig,ratio_center);
let img_bkg;


let fname_task1 = '../img/task1.png';
let fname_task2 = '../img/task2.png';
let fname_instruct1 = '../img/instruction1.png';
let fname_instruct2 = '../img/instruction2.png';

let flag_practice = true;
let flag_break = true;
let count_break = 0;
let max_break = 1;

let num_rep_main = 10; 
let num_rep_practice = 1;

let array_stimcond = [1,1,1,1,0,0,0,0];
let array_target = [1,2,3,4,6,7,8,9];
let array_taskcond = ['Color','Shape']; //Tasks switch condition.
let array_textleft = ['Red:f','Circle:f'];
let array_textright = ['Blue:j','Square:j']; 
let array_colorcond = [0,1]; //0:color 0, 1:color 1
let array_shapecond = [0,1]; //0:Circle, 1:Square
let col_0 =[128,0,0];
let col_1 = [0,0,128];

let keyRes1 = 70; //f
let keyRes2 = 74; //j

let time_stimduration = 4000; //in ms
//let time_maskduration = 1000; //in ms
let time_maskduration = 0; //in ms
let time_fixation = 650; // in millisecond

//object condition
let size_obj = Math.round(7*ppd); //in pix. in diameter
let size_instruct_x = Math.round(10*ppd); //in pix. in diameter
let size_instruct_y = Math.round(2*ppd); //in pix. in diameter
let x_instruct = Pos.center_x-(size_instruct_x/2);
let y_instruct = (Pos.canvas_height*ratio_monitor)-(size_instruct_y/2)-Math.round(1*ppd);
let text_1left = "Odd";
let text_1right = "Even";
let text_2left = "Low";
let text_2right = "High";
let size_instruct_txt = Math.round(0.6*ppd);
let x_instruct_text1 = Pos.center_x-(size_instruct_x/4);
let y_instruct_text = (Pos.canvas_height*ratio_monitor)+(size_instruct_txt/2)-Math.round(1*ppd);
let x_instruct_text2 = Pos.center_x+(size_instruct_x/4);

// fixation 
let col_instruction = 255;
let size_instruction = Math.round(1.5*ppd); //in pix


// text 
let col_text = 255;
let size_text = Math.round(0.7*ppd); //in pixel
////

let col_bkg = 0;

let x_ok = -Math.round(0*ppd);
let y_ok = Math.round(4*ppd);
let x_restart = -Math.round(5.5*ppd);; //in pixel
let y_restart = -Math.round(4*ppd);; //in pixel



let text_start = "Please click the mouse to start this experiment";
let text_end = "Thank you for joining the experiment.";