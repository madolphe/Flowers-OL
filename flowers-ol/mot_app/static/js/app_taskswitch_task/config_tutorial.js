//general title text
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
let y_next = Pos.center_y+Math.round(5*ppd)+(size_next_h/2); //in pixel
let size_next_text = Math.round(0.5*ppd);

let size_previous_w = Math.round(2.5*ppd); //in pixel
let size_previous_h = Math.round(1.5*ppd); //in pixel
let x_previous = Pos.center_x-Math.round(4*ppd)-(size_previous_w/2); //in pixel
let y_previous = Pos.center_y+Math.round(5*ppd)+(size_previous_h/2); //in pixel
let size_previous_text = Math.round(0.5*ppd); //in pixel

//scene 0 
let text_tutorial_0_0 = "The goal of this experiment is to measure the ability ";
let text_tutorial_0_1 = "to switch your attention. On each trial, you will see a digit ";
let text_tutorial_0_2 = "from the set {1– 4, 6–9} on the cue background of red or blue."; 
let text_tutorial_0_3 = "Your tasks change with the cue background.";
let pos_tutorialtext_x = Pos.center_x;
let pos_tutorialtext_y = Pos.center_y;
let size_tutorialtext = Math.round(0.8*ppd);
// let col_tutorialtext = [220,220,255];
let col_tutorialtext = "white";
let shift_text = Math.round((1*ppd));

//scene 1
let flag_disp = false;
let num_demotargnum = 5;

let text_tutorial_1_0 = "When the cue is the blue diamond-shaped background,";
let text_tutorial_1_1 = "you have to answer whether the target digit was odd or even";
let text_tutorial_1_2 = "by using the key [F] or [J], respectively."; 
let pos_tutorialtext_x1 = Pos.center_x;
let pos_tutorialtext_y1 = Pos.center_y;
let pos_image_y1 = Pos.center_y-Math.round(9.5*ppd);
let pos_image_2_y1 = Pos.center_y-Math.round(2.8*ppd);
let y_instruct_text_tuto = pos_image_2_y1 + 2*(size_instruct_txt);

//scene 2
let text_tutorial_2_0 = "When the cue is the red square background, you have";
let text_tutorial_2_1 = "to answer whether the target digit was lower or higher than 5";
let text_tutorial_2_2 = "by using the key [F] or [J], respectively."; 
let pos_tutorialtext_x2 = Pos.center_x;
let pos_tutorialtext_y2 = Pos.center_y;

//scene 3
let text_tutorial_3_0 = "Let's start the practices.";
let size_tutorialtext3 = Math.round(1*ppd);
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

