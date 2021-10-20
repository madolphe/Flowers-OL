// 3 Functions to handle inputs (init, size and position)
function init_pannel(){
    // Start with pannel status : hidden
    hidden_pannel = true;

    // Create all inputs:
    button_params = createButton('RESTART');
    button_raz_params = createButton('DEFAULT');
    button_hide_params = createButton('>>');
    button_hide_params.mousePressed(switch_pannel_status);
    button_raz_params.mousePressed(raz);
    button_params.mousePressed(restart);
    screen_params_input = createInput(parameter_dict['screen_params']);
    angle_max_input = createInput(parameter_dict['angle_max']);
    angle_min_input = createInput(parameter_dict['angle_min']);
    debug_input = createInput(parameter_dict['debug']);
    secondary_task_input = createInput(parameter_dict['secondary_task']);
    n_targets_input = createInput(parameter_dict['n_targets']);
    n_distractors_input = createInput(parameter_dict['n_distractors']);
    speed_max_input = createInput(parameter_dict['speed_max']);
    speed_min_input = createInput(parameter_dict['speed_min']);
    radius_input = createInput(parameter_dict['radius']);
    presentation_time_input = createInput(parameter_dict['presentation_time']);
    fixation_time_input = createInput(parameter_dict['fixation_time']);
    tracking_time_input = createInput(parameter_dict['tracking_time']);
    SRI_max_input = createInput(parameter_dict['SRI_max']);
    RSI_input = createInput(parameter_dict['RSI']);
    delta_orientation_input = createInput(parameter_dict['delta_orientation']);
    gaming_input = createInput(parameter_dict['gaming']);

    // Add some widgets:
    n_targets_slider = createSlider(0,15,1);
    angle_max_slider = createSlider(1,15, 1);
    angle_min_slider = createSlider(0,10, 1);
    n_distractors_slider = createSlider(0, 15, 1);
    speed_max_slider = createSlider(0.5, 10, 0.2);
    speed_min_slider = createSlider(0.5, 10, 0.2);
    radius_slider = createSlider(0.5, 2, 1, 0.2);
    presentation_time_slider = createSlider(0.5, 30, 0.5);
    fixation_time_slider = createSlider(0.5, 30, 0.5);
    tracking_time_slider = createSlider(0.5, 30, 0.5);
    SRI_max_slider = createSlider(0.5, 30, 0.5);
    RSI_slider = createSlider(0.1, 10, 0.1);
    delta_orientation_slider = createSlider(0,85, 1);

    // Input description:
    screen_params_description = "Dimension of your screen diagonal (in cm)";
    angle_max_description = "Maximum angle characterizing the \"outer\" limit of the scene (in deegres)";
    angle_min_description = "Minimum angle characterizing the \"inner\" limit of the scene (in deegres)";
    debug_description = "Debug mode (0 or 1, no or yes)";
    secondary_task_description = "Play the game with a secondary task (none, detection or discrimination)";
    n_targets_description = "Number of targets to track";
    n_distractors_description = "Number of distractors to track";
    speed_max_description = "Maximum speed (in deegres per sec)";
    speed_min_description = "Minimum speed (in deegres per sec)";
    radius_description = "Maximum distance around an object i.e distance for collision (in pixels)";
    presentation_time_description = "Duration of presentation phase i.e objects are moving and displayed on their respective roles (in sec)";
    fixation_time_description = "Duration of fixation phase i.e objects are fixed and are displayed on their respective roles (in sec)";
    tracking_time_description = "Duration of tracking phase i.e objects are moving while displayed all the same (in sec)";
    SRI_max_description = "Maximum duration of interval between 2 secondary task (in sec)";
    RSI_description = "Duration of the display of one secondary task (in sec)";
    delta_orientation_description = "Orientation of leaves in the secondary task image only for detection mode (in degrees)";
    gaming_description = "Choose to play in a gaming mode (1 or 0)";

    // Dictionnary to store all objects in one
    dict_pannel =  {
        gaming : {gaming_input, gaming_description},
        screen_params : {screen_params_input, screen_params_description},
        angle_max : {angle_max_input, angle_max_slider, angle_max_description},
        angle_min : {angle_min_input, angle_min_slider, angle_min_description},
        debug: {debug_input, debug_description},
        secondary_task: {secondary_task_input, secondary_task_description},
        n_targets: {n_targets_input, n_targets_slider, n_targets_description},
        n_distractors: {n_distractors_input, n_distractors_slider, n_distractors_description},
        speed_max: {speed_max_input, speed_max_slider, speed_max_description},
        speed_min: {speed_min_input, speed_min_slider, speed_min_description},
        radius: {radius_input, radius_slider, radius_description},
        presentation_time: {presentation_time_input, presentation_time_slider, presentation_time_description},
        fixation_time: {fixation_time_input, fixation_time_slider, fixation_time_description},
        tracking_time: {tracking_time_input, tracking_time_slider, tracking_time_description},
        SRI_max: {SRI_max_input, SRI_max_slider, SRI_max_description},
        RSI: {RSI_input, RSI_slider, RSI_description},
        delta_orientation: {delta_orientation_input, delta_orientation_slider, delta_orientation_description}
    };
    // Hide all inputs:
    hide_inputs();
    button_hide_params.hide();
    position_inputs();
    size_inputs();
}
function size_inputs(){
    //inputs_map.forEach(function(value, key, map){value.size(windowHeight/10, step*(2/3))});
    for (var key in dict_pannel) {
        // check if the property/key is defined in the object itself, not in parent
        if (dict_pannel.hasOwnProperty(key)) {
            dict_pannel[key][key+'_input'].size(windowHeight/20, step*(2/3));
                if(!dict_pannel[key].hasOwnProperty(key+'_slider')) {
                dict_pannel[key][key+'_input'].size(windowHeight/10, step*(2/3));
            }
        }
    }
}
function position_inputs(){
    step = windowHeight/25;
    let start = 150;
    let i = 0;
    for (var key in dict_pannel) {
        // check if the property/key is defined in the object itself, not in parent
        if (dict_pannel.hasOwnProperty(key)) {
            dict_pannel[key][key+'_input'].position(start,  windowHeight - step * (Object.keys(dict_pannel).length - i+3));
            dict_pannel[key].position = (windowHeight - step * (Object.keys(dict_pannel).length - i+3));
            if(dict_pannel[key].hasOwnProperty(key+'_slider')) {
                dict_pannel[key][key+'_slider'].position(start+60,  windowHeight - step * (Object.keys(dict_pannel).length - i+3));
            }
        }
        i++;
    }
    // Position for visible pannel:
    button_params.position(start/4, windowHeight - 2.8*step);
    button_raz_params.position(4*start/4, windowHeight - 2.8*step);
    button_hide_params.position(10, windowHeight/2);
}

// Functions used by p5 to display
function display_pannel(){
    if(!hidden_pannel){
    push();
    fill('white');
    rectMode(CORNERS);
    textAlign(CENTER);
    textFont(gill_font);
    textSize(15);
    let i = 1;
    for(var key in dict_pannel){
        text(key, 0, windowHeight - step*(Object.keys(dict_pannel).length-(i-4)), 150, step);
        i ++;
    }
    pop();
    add_hover();
    push();
    fill('white');
    textFont(gill_font);
    rectMode(CORNERS);
    textAlign(CENTER);
    textSize(20);
    textStyle(BOLD);
    text("PARAMETERS:", 0, windowHeight - step * 21, 150, step);
    pop();
    }
}
function add_hover(){
    for(var key in dict_pannel){
        if(mouseX<350){
            if(mouseY>dict_pannel[key].position){
                if(mouseY<dict_pannel[key].position+step){
                    push();
                    strokeWeight(2);
                    stroke('white');
                    fill(0,0,0,100);
                    rectMode(CORNERS);
                    rect(350, dict_pannel[key].position, 700, dict_pannel[key].position+step);
                    pop();
                    push();
                    fill('white');
                    textFont(gill_font);
                    textSize(14);
                    textAlign(CENTER, CENTER);
                    text(dict_pannel[key][key+'_description'], 350, dict_pannel[key].position, 350, step);
                    pop();
                }
            }
            }
        }
}

// Functions used for user interaction
function hide_inputs(){
    button_params.hide();
    button_raz_params.hide();
    for (var key in dict_pannel) {
        // check if the property/key is defined in the object itself, not in parent
        if (dict_pannel.hasOwnProperty(key)) {
            dict_pannel[key][key+'_input'].hide();
            if(dict_pannel[key].hasOwnProperty(key+'_slider')){
                dict_pannel[key][key+'_slider'].hide();
            }
        }
    }
}
function show_inputs(){
    button_hide_params.show();
    button_raz_params.show();
    button_params.show();
    for (var key in dict_pannel) {
        if (dict_pannel.hasOwnProperty(key)) {
            dict_pannel[key][key+'_input'].show();
                if(dict_pannel[key].hasOwnProperty(key+'_slider')) {
                dict_pannel[key][key+'_slider'].show();
            }
        }
    }
}
function switch_pannel_status(){
    if(!hidden_pannel){
        button_hide_params.elt.innerHTML = '>>';
        button_hide_params.position(10, windowHeight/2);
        hide_inputs();
    }else{
        button_hide_params.elt.innerHTML = 'HIDE <<';
        button_hide_params.position(7*150/4, windowHeight - 2.8*step);
        show_inputs();
    }
    hidden_pannel = !hidden_pannel;
}
function update_input_from_slider_value(){
    // Function launch whenever a mouse is released
    // Update input value depending on slider:
    if(dict_pannel){
        for(var key in dict_pannel){
            if(dict_pannel[key].hasOwnProperty(key+'_slider')){
                dict_pannel[key][key+'_input'].value(dict_pannel[key][key+'_slider'].value())
            }
        }
    }
}
function update_parameters_values(){
    for (var key in dict_pannel) {
        // check if the property/key is defined in the object itself, not in parent
        if (dict_pannel.hasOwnProperty(key)) {
            dict_pannel[key][key+'_input'].value(parameter_dict[key]);
            if(dict_pannel[key].hasOwnProperty(key+'_slider')) {
                dict_pannel[key][key+'_slider'].value(parameter_dict[key]);
            }
        }
    }
}
function restart(){
    // First update parameter_dict with new values in admin_pannel
    for(var key in dict_pannel){
        if(parameter_dict.hasOwnProperty(key)){
            if(!dict_pannel[key].hasOwnProperty(key+'_slider')){
                parameter_dict[key] = dict_pannel[key][key+'_input'].value();
            }else{
                parameter_dict[key] = parseFloat(dict_pannel[key][key+'_input'].value());
            }
        }
    }
    // Send ajax_request
    $.ajax({
        async: false,
        type: "POST",
        url: "/restart_episode",
        dataType: "json",
        traditional: true,
        data: parameter_dict,
        success: function(data) {
            parameter_dict = data;
            console.log(parameter_dict);
            }
        });
    // update screen params and timers
    set_screen_params();
    clearTimeout(pres_timer);
    clearTimeout(tracking_timer);
    clearTimeout(answer_timer);
    clearTimeout(probe_timer);
    // make sure buttons are hidden to restart
    if(button_next_episode){
        button_next_episode.hide();
    }
    if(button_answer){
        button_answer.hide();
    }
    start_episode();
}
function raz(){
    // No more useless call to backend:
    Object.keys(default_params).forEach(function(key) {
        parameter_dict[key] = default_params[key]
    });
    set_screen_params();
    clearTimeout(pres_timer);
    clearTimeout(tracking_timer);
    clearTimeout(answer_timer);
    clearTimeout(probe_timer);
    if(button_next_episode){
        button_next_episode.hide();
    }
    if(button_answer){
        button_answer.hide();
    }
    start_episode();
}
