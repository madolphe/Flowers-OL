//general title text
let text_title_0 = "Instruction";
let pos_title_x = Pos.center_x;
let pos_title_y = Pos.center_y - Math.round(5*ppd);
let size_titletext = Math.round(2.5*ppd);
let col_titletext = [170,170,60];

//general button
let size_next_w = Math.round(2.5*ppd); //in pixel
let size_next_h = Math.round(1.5*ppd); //in pixel
let x_next = Pos.center_x+Math.round(6*ppd)-(size_next_w/2); //in pixel
let y_next = Pos.canvas_height-Math.round(2*ppd)-(size_next_h/2); //in pixel
let size_next_text = Math.round(0.5*ppd);

let size_previous_w = Math.round(2.5*ppd); //in pixel
let size_previous_h = Math.round(1.5*ppd); //in pixel
let x_previous = Pos.center_x-Math.round(6*ppd)-(size_previous_w/2); //in pixel
let y_previous = Pos.canvas_height-Math.round(2*ppd)-(size_next_h/2); //in pixel
let size_previous_text = Math.round(0.5*ppd); //in pixel

//scene 0 
let text_tutorial_0_0 = "The goal of this experiment is to measure the attention ability";
let text_tutorial_0_1 = "to multiple targets. On each trial, you will see";
let text_tutorial_0_2 = "a brief presentation of a cross target with four stripe objects."; 
let text_tutorial_0_3 = "You have to answer two tasks for each trial.";
let pos_tutorialtext_x = Pos.center_x;
let pos_tutorialtext_y = Pos.center_y;
let size_tutorialtext = Math.round(0.5*ppd);
let col_tutorialtext = [220,220,255];
let shift_text = Math.round((1*ppd));

//scene 1
let flag_disp = false;
let num_demotargnum = 5;

let text_tutorial_1_0 = "This is an example of stimulus presentation.";
let pos_tutorialtext_x1 = Pos.center_x;
let pos_tutorialtext_y1 = Pos.center_y-Math.round(6*ppd);

//scene 2
let text_tutorial_2_0 = "First, you have to answer which of the lines was longer.";
let pos_tutorialtext_x2 = Pos.center_x;
let pos_tutorialtext_y2 = Pos.center_y-Math.round(6*ppd);

//scene 2_2
let text_tutorial_2_1 = "Next, you have to answer which of the four objects had the strong contrast";

//scene 3
let text_tutorial_3_0 = "Let's start the practices.";
let text_tutorial_3_1 = "Please keep in mind that you have to correctly answer";
let text_tutorial_3_2 = "at least the first length question.";
let size_tutorialtext3 = Math.round(1*ppd);
let pos_tutorialtext_x3 = Pos.center_x;
let pos_tutorialtext_y3 = Pos.center_y-Math.round(2.5*ppd);

let size_start_w = Math.round(2.5*ppd); //in pixel
let size_start_h = Math.round(1.5*ppd); //in pixel
let x_start = Pos.center_x- (size_start_w/2); //in pixel
let y_start = Pos.center_y+Math.round(2*ppd)-(size_start_h/2); //in pixel
let size_start_text = Math.round(0.5*ppd);

//scene main ready
let text_tutorial_4_0 = "Let's start the main experiment.";
//scene break
let text_tutorial_5_0 = "Break time.";

