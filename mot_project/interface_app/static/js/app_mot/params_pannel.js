function init_pannel(){
    button_params = createButton('RESTART');
    screen_params_input = createInput(diagcm);
    angle_max_input = createInput(parameter_dict['angle_max']);
    angle_min_input = createInput(parameter_dict['angle_max']);
    debug_input = createInput(str(parameter_dict['debug']));
    activity_type_input = createInput(parameter_dict['secondary_task']);
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
    labels_inputs = ["Parameters", "screen_params_input", "angle_max_input", "angle_min_input",
        "debug_input","activity_type_input", "n_targets_input", "n_distractors_input", "speed_max_input",
        "speed_min_input", "radius_input", "presentation_time_input", "fixation_time_input",
        "tracking_time_input", "SRI_max_input", "RSI_input", "delta_orientation_input"];
    key_val = [["screen_params_input", screen_params_input], ["angle_max_input",angle_max_input],
        ["angle_min_input", angle_min_input], ["debug_input", debug_input],["activity_type_input", activity_type_input],
        ["n_targets_input", n_targets_input], ["n_distractors_input", n_distractors_input],
        ["speed_max_input", speed_max_input], ["speed_min_input", speed_min_input],
        ["radius_input", radius_input], ["presentation_time_input", presentation_time_input],
        ["fixation_time_input", fixation_time_input], ["tracking_time_input", tracking_time_input],
        ["SRI_max_input", SRI_max_input], ["RSI_input", RSI_input], ["delta_orientation_input", delta_orientation_input]];
    inputs_map = new Map(key_val);
    hide_inputs();
}
function hide_inputs(){
    inputs_map.forEach(function(value, key, map){value.hide()});
    button_params.hide();
}
function show_inputs(){
    inputs_map.forEach(function(value, key, map){value.show()});
    button_params.show();
    button_params.mousePressed(restart);
}
function size_inputs(){
    inputs_map.forEach(function(value, key, map){value.size(windowHeight/10, step*(2/3))});
}
function position_inputs(){
    step = windowHeight/25;
    let start = 150;
    let i = 0;
    inputs_map.forEach(function(value, key){
        value.position(start,  windowHeight - step * (labels_inputs.length - i+3));
        i++;
    });
    button_params.position(start/2, windowHeight - 3.5*step)
}
function display_pannel(){
    push();
    fill('white');
    rectMode(CORNERS);
    textAlign(CENTER);
    for(let i = 1; i<labels_inputs.length; i++){
        text(labels_inputs[i], 0, windowHeight - step*(labels_inputs.length-(i-4)), 150, step)
    }
    pop();
    push();
    fill('white');
    rectMode(CORNERS);
    textAlign(CENTER);
    textSize(20);
    text("Parameters:", 0, windowHeight - step * 21, 150, step);
    pop();
}

function update_parameters_values(){
    screen_params_input.value(diagcm);
    angle_max_input.value(parameter_dict['angle_max']);
    angle_min_input.value(parameter_dict['angle_min']);
    debug_input.value(str(parameter_dict['debug']));
    activity_type_input.value(parameter_dict['secondary_task']);
    n_targets_input.value(parameter_dict['n_targets']);
    n_distractors_input.value(parameter_dict['n_distractors']);
    speed_max_input.value(parameter_dict['speed_max']);
    speed_min_input.value(parameter_dict['speed_min']);
    radius_input.value(parameter_dict['radius']);
    presentation_time_input.value(parameter_dict['presentation_time']);
    fixation_time_input.value(parameter_dict['fixation_time']);
    tracking_time_input.value(parameter_dict['tracking_time']);
    SRI_max_input.value(parameter_dict['SRI_max']);
    RSI_input.value(parameter_dict['RSI']);
    delta_orientation_input.value(parameter_dict['delta_orientation']);
}

function restart(){
    parameter_dict['screen_params'] = int(screen_params_input.value());
    parameter_dict['angle_max'] = int(angle_max_input.value());
    parameter_dict['angle_min'] =  int(angle_min_input.value());
    parameter_dict['debug'] =  int(debug_input.value());
    parameter_dict['activity_type'] =  activity_type_input.value();
    parameter_dict['n_targets'] =  int(n_targets_input.value());
    parameter_dict['n_distractors'] =  int(n_distractors_input.value());
    parameter_dict['speed_max'] =  int(speed_max_input.value());
    parameter_dict['speed_min'] =  int(speed_min_input.value());
    parameter_dict['radius'] = int(radius_input.value());
    parameter_dict['presentation_time'] =  int(presentation_time_input.value());
    parameter_dict['fixation_time'] =  int(fixation_time_input.value());
    parameter_dict['tracking_time'] =  int(tracking_time_input.value());
    parameter_dict['SRI_max'] =  int(SRI_max_input.value());
    parameter_dict['RSI'] =  int(RSI_input.value());
    parameter_dict['delta_orientation'] =  int(delta_orientation_input.value());
    console.log("before ajax", parameter_dict);
    $.ajax({
    async: false,
    type: "POST",
    url: "/restart_episode",
    dataType: "json",
    traditional: true,
    data: parameter_dict,
    success: function(data) {
        parameter_dict = data;
        console.log("AJAX response", parameter_dict)
        }
    });
    clearTimeout(pres_timer);
    clearTimeout(tracking_timer);
    clearTimeout(answer_timer);
    if(button_next_episode){
        button_next_episode.hide();
    }
    if(button_answer){
        button_answer.hide();
    }
    start_episode();
}

function old() {
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
    RSI_input.hide();
    delta_orientation_input.hide();
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
    screen_params_input.position(start, windowHeight - step * 20);
    angle_max_input.position(start, windowHeight - step * 19);
    angle_min_input.position(start, windowHeight - step * 18);
    debug_input.position(start, windowHeight - step * 17);
    activity_type_input.position(start, windowHeight - step * 16);
    n_targets_input.position(start, windowHeight - step * 15);
    n_distractors_input.position(start, windowHeight - step * 14);
    speed_max_input.position(start, windowHeight - step * 13);
    speed_min_input.position(start, windowHeight - step * 12);
    radius_input.position(start, windowHeight - step * 11);
    presentation_time_input.position(start, windowHeight - step * 10);
    fixation_time_input.position(start, windowHeight - step * 9);
    tracking_time_input.position(start, windowHeight - step * 8);
    SRI_max_input.position(start, windowHeight - step * 7);
    RSI_input.position(start, windowHeight - step * 6);
    delta_orientation_input.position(start, windowHeight - step * 5);
}
