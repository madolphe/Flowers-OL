//// parameters

// number of pixels per degres:
let viewer_dist = 50;
let screen_params = 1920/34.25; // width pixels/cm in sawayama's monitor
let ppd = get_ppd(viewer_dist, screen_params);

function get_ppd(viewer_dist, screen_params){
    return (viewer_dist*Math.tan(Math.PI/180)) * screen_params;
}

//console.log(ppd) //48.925 in my screen
//const CANVAS_WIDTH = 640;
//const CANVAS_HEIGHT = 480;

let num_rep = 20; 
let array_stimcond = [5,6,7,8,9]; //Experimental condition. 
let time_stimduration = 50; //in ms Green & Bavelier (2006)
let time_maskduration = 1000; //in ms

//object condition
let size_obj = Math.round(0.5*ppd); //in pix. in diameter
let roi_obj = Math.round(10*ppd); //in pix. in diameter. Later, these value will be determined from the visual angle.
let Objs = [];

//save array. just be stored in the prensetation order.
let array_responses =[];
let array_stimuli =[];

// for the mask image
let img;
let size_img = [1024,1024];

// fixation 
let len_fixation = Math.round(1*ppd); // in pix
let col_fixation = 20; // in rgb
let thick_fixation = Math.round(0.1*ppd); // in pix
let time_fixation = 1000; // in millisecond

// text 
let col_text = 255;
let size_text = Math.round(1*ppd); //in pixel

//button
let sel;
let x_response = 50;
let y_response = 200;
let max_answer = 15;
let x_ok = -50;
let y_ok = 200;
let round_button = "5px";
let size_button_x = "70px";
let size_button_y = "70px";
////

