function init_pannel(){
    screen_params_input = createInput("screen_params_input");
    angle_max_input = createInput();
    angle_min_input = createInput();
    debug_input = createInput();
    activity_type_input = createInput();
    n_targets_input = createInput();
    n_distractors_input = createInput();
    speed_max_input = createInput();
    speed_min_input = createInput();
    radius_input = createInput();
    presentation_time_input = createInput();
    fixation_time_input = createInput();
    tracking_time_input = createInput();
    SRI_max_input = createInput();
    RSI_input = createInput();
    delta_orientation_input = createInput("delta_orientation_input");
    hide_inputs();
}
function hide_inputs(){
    screen_params_input.hide();
    angle_max_input.hide();
    angle_min_input.hide();
    debug_input.hide();
    activity_type_input.hide();
    n_targets_input.hide();
    n_distractors_input.hide();
    speed_max_input.hide();
    speed_min_input.hide();
    radius_input.hide();
    presentation_time_input.hide();
    fixation_time_input.hide();
    tracking_time_input.hide();
    SRI_max_input.hide();
    RSI_input .hide();
    delta_orientation_input.hide();
}
function show_inputs(){
    screen_params_input.show();
    angle_max_input.show();
    angle_min_input.show();
    debug_input.show();
    activity_type_input.show();
    n_targets_input.show();
    n_distractors_input.show();
    speed_max_input.show();
    speed_min_input.show();
    radius_input.show();
    presentation_time_input.show();
    fixation_time_input.show();
    tracking_time_input.show();
    SRI_max_input.show();
    RSI_input.show();
    delta_orientation_input.show();
}
function position_inputs(){
    step = windowHeight/25;
    let start = 150;
    screen_params_input.position(start,windowHeight-step*16);
    angle_max_input.position(start, windowHeight-step*15);
    angle_min_input.position(start, windowHeight-step*14);
    debug_input.position(start, windowHeight-step*13);
    activity_type_input.position(start, windowHeight-step*12);
    n_targets_input.position(start, windowHeight-step*11);
    n_distractors_input.position(start, windowHeight-step*10);
    speed_max_input.position(start, windowHeight-step*9);
    speed_min_input.position(start, windowHeight-step*8);
    radius_input.position(start, windowHeight-step*7);
    presentation_time_input.position(start, windowHeight-step*6);
    fixation_time_input.position(start, windowHeight-step*5);
    tracking_time_input.position(start, windowHeight-step*4);
    SRI_max_input.position(start, windowHeight-step*3);
    RSI_input.position(start, windowHeight-step*2);
    delta_orientation_input.position(start, windowHeight-step);
}
function display_pannel(){
    push();
    fill('white');
    rectMode(CORNERS);
    textAlign(CENTER);
    text("screen_params_input",0 ,windowHeight-step*16, 150, step);
    text("angle_max_input", 0, windowHeight-step*15, 150, step);
    text("angle_min_input", 0, windowHeight-step*14, 150, step);
    text("debug_input", 0, windowHeight-step*13, 150, step);
    text("activity_type_input", 0, windowHeight-step*12, 150, step);
    text("n_targets_input", 0, windowHeight-step*11, 150, step);
    text("n_distractors_input", 0, windowHeight-step*10, 150, step);
    text("speed_max_input", 0, windowHeight-step*9, 150, step);
    text("speed_min_input", 0, windowHeight-step*8, 150, step);
    text("radius_input", 0, windowHeight-step*7, 150, step);
    text("presentation_time_input", 0, windowHeight-step*6, 150, step);
    text("fixation_time_input", 0, windowHeight-step*5, 150, step);
    text("tracking_time_input", 0, windowHeight-step*4, 150, step);
    text("SRI_max_input", 0, windowHeight-step*3, 150, step);
    text("RSI_input", 0, windowHeight-step*2, 150, step);
    text("delta_orientation_input", 0, windowHeight-step, 150, step);
    //rect( 0, windowHeight-step, 150, windowHeight);
    pop();
}