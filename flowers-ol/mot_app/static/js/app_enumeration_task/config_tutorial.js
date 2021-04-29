//general title text
//let text_title_0 = "Instruction";
let text_title_0 = "INSTRUCTIONS";
let pos_title_x = Pos.center_x;
let pos_title_y = Pos.center_y - Math.round(5*ppd);
let size_titletext = Math.round(2.5*ppd);
//let col_titletext = [170,170,60];
let col_titletext = 'white';

//general button
let size_next_w = Math.round(2.5*ppd); //in pixel
let size_next_h = Math.round(1.5*ppd); //in pixel
let x_next = Pos.center_x+Math.round(4*ppd)-(size_next_w/2); //in pixel
let y_next = Pos.canvas_height-Math.round(3*ppd)-(size_next_h/2); //in pixel
let size_next_text = Math.round(0.5*ppd);

let size_previous_w = Math.round(2.5*ppd); //in pixel
let size_previous_h = Math.round(1.5*ppd); //in pixel
let x_previous = Pos.center_x-Math.round(4*ppd)-(size_previous_w/2); //in pixel
let y_previous = Pos.canvas_height-Math.round(3*ppd)-(size_previous_h/2); //in pixel
let size_previous_text = Math.round(0.5*ppd); //in pixel

let text_font = 'Helvetica';

//scene 0 
let text_tutorial_0_0 = "The goal of this experiment is to measure your counting ability.";
let text_tutorial_0_1 = "On each trial, you will see a brief flash of multiple white circles.";
let text_tutorial_0_2 = "Your task is to count these circles and answer how many circles"; 
let text_tutorial_0_3 = "were presented using a slider bar.";
let pos_tutorialtext_x = Pos.center_x - window_availw/4
let pos_tutorialtext_y = Pos.center_y;
let size_tutorialtext = Math.round(0.8*ppd);
//let col_tutorialtext = [220,220,255];
let col_tutorialtext = 'white';
let shift_text = Math.round((1*ppd));

//scene 1
let flag_disp = false;
let num_demotargnum = 5;

let text_tutorial_1_0 = "Please remember the number of these white circles.";
let pos_tutorialtext_x1 = Pos.center_x;
//let pos_tutorialtext_y1 = Pos.center_y-Math.round(5*ppd);
let pos_tutorialtext_y1 = Pos.center_y+Math.round(2*ppd);
let pos_tutorialimage_y1 = Pos.center_y - Math.round(4*ppd);
let pos_tutorialslider_y1 = Pos.center_y - Math.round(3*ppd)

//scene 2
let text_tutorial_2_0 = "Please answer how many circles were presented using a slider bar";
let pos_tutorialtext_x2 = Pos.center_x;
let pos_tutorialtext_y2 = Pos.center_y+Math.round(2*ppd);
// let pos_anszer_y2= Pos.center_y+(size_answer/2)
let pos_answer_y2= Pos.center_y - 5*ppd;


//scene 3
let text_tutorial_3_0 = "Let's start the practices.";
let size_tutorialtext3 = Math.round(0.8*ppd);
let pos_tutorialtext_x3 = Pos.center_x;
let pos_tutorialtext_y3 = Pos.center_y-Math.round(0*ppd);

let size_start_w = Math.round(2.5*ppd); //in pixel
let size_start_h = Math.round(1.5*ppd); //in pixel
let x_start = Pos.center_x- (size_start_w/2); //in pixel
let y_start = Pos.center_y+Math.round(2*ppd)-(size_start_h/2); //in pixel
let size_start_text = Math.round(0.5*ppd);

//scene main ready
let text_tutorial_4_0 = "Let's start the main experiment.";
//scene break
let text_tutorial_5_0 = "Break time.";