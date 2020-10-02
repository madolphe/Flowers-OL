let cross_length = 10;
let radius;
let message = '';
let fill_bar_size = 0;
let show_probe_timer = false;
let game_end = false;
let min, sec;

// main function used to display :
function play(disp_zone){
    // Then display game dynamics:
    display_game_timer();
    display_fixation_cross(cross_length);
    if(disp_zone){
        display_game_zone(3, 9);
    }
    if(!paused){
        app.display_objects(mouseX, mouseY);
        app.check_collisions();
        app.move_objects();
        if(parameter_dict['gaming']!=0){
            if(parameter_dict['secondary_task']!='none'){
                sec_task.display_task();
            }
        }
        if(parameter_dict['admin_pannel']){
            display_pannel();
        }
        if(show_probe_timer){
            display_probe_timer();
        }
    }else{
        button_keep.show();
        display_transition();
    }
    if(bot_mode){
       bot_answer(app);
    }
}
function display_game_zone(){
    push();
    ellipseMode(CENTER);
    stroke('red');
    noFill();
    strokeWeight(4);
    radius = Math.round(ppd*max_angle);
    ellipse(windowWidth/2, windowHeight/2, radius);
    pop();
    push();
    ellipseMode(CENTER);
    stroke('red');
    noFill();
    strokeWeight(2);
    radius = Math.round(ppd*min_angle);
    ellipse(windowWidth/2, windowHeight/2, radius);
    pop();
}
function display_fixation_cross(cross_length){
    push();
    stroke('black');
    strokeWeight(2);
    rectMode(CENTER);
    fill(10,10,10,100);
    rect(windowWidth/2, windowHeight/2, cross_length, cross_length);
    pop();
}
function display_probe_timer(){
    if(fill_bar_size<300){
        fill_bar_size = fill_bar_size + (300/(parameter_dict['probe_time']*30))
    }
    push();
    textFont(gill_font_light);
    textSize(25);
    textStyle(BOLD);
    fill('white');
    textAlign(CENTER, TOP);
    rectMode(CORNERS);
    text("TEMPS RESTANT:", 70, 70, 200, 200);
    color('white');
    stroke(255);
    strokeWeight(3);
    noFill();
    rect(270,70,570,90);
    pop();
    push();
    fill('white');
    noStroke();
    rectMode(CORNERS);
    rect(270,70,270+fill_bar_size,90);
    pop();
}
function display_transition(){
    let width = 170;
    let height = 70;
    push();
    fill(250,250,250,210);
    rectMode(CENTER);
    rect(windowWidth/2, windowHeight/2, windowWidth, 500);
    button_keep.show();
    textFont(gill_font_light);
    textSize(25);
    textStyle(BOLD);
    fill('black');
    textAlign(CENTER, TOP);
    rectMode(CORNERS);
    text(message, 0, windowHeight/2 - height, windowWidth, 2*height);
    pop();
}
function display_game_timer() {
    min = Math.floor(game_time / 60);
    // Game_time / 2 as update is made every 0.5s (ie 30 fps)
    sec = Math.floor(game_time - (min*60));
    push();
    translate(windowWidth-300,windowHeight-80);
    imageMode(CENTER);
    scale(0.1);
    image(timer_image, 0, 0);
    pop();
    push();
    textFont(gill_font_light);
    textSize(25);
    textStyle(BOLD);
    fill('white');
    textAlign(CENTER, CENTER);
    rectMode(CORNER);
    text("Fin du jeu: " + str(min) + ':' + str(sec), windowWidth-310, windowHeight-150, 300, 150);
    pop();
}
// Functions to manage game time:
function timer_end_game(){
    game_timer = setTimeout(function(){
        game_end = true;
        quit_game();
    }, parameter_dict['game_time']*1000)
}
function timer(app, presentation_time, fixation_time, tracking_time, probe_time){
    pres_timer = setTimeout(function () {
        // after presention_time ms
        // app.phase changes to fixation
        app.phase = 'fixation';
        app.frozen = true;
        // and stay in this frozen mode for fixation_time ms
        tracking_timer = setTimeout(function(){
            // after fixation_time ms
            // app.phase change to tracking mode
            if(parameter_dict['gaming']!=0 && parameter_dict['secondary_task']!='none') {
                sec_task.timer_pause();
            }
            app.phase = 'tracking';
            app.frozen = false;
            app.change_to_same_color();
            // and stay in this mode for tracking_time ms
           answer_timer = setTimeout(function(){
                // after tracking_time ms, app changes to answer phase
                app.phase = 'answer';
                app.frozen = true;
                app.enable_interact();
                show_answer_button();
                show_probe_timer = true;
                probe_timer = setTimeout(function () {
                    answer_button_clicked()
                },
                    probe_time)},
                tracking_time)},
            fixation_time)},
        presentation_time);
}

// functions to parametrized game, timer and user interactions:
function start_episode(){
    // Some variable for transition, probe_timer..:
    message = '';
    fill_bar_size = 0;
    show_probe_timer = false;
    paused = false;
    button_keep.hide();
    // Init the proper app (gamin mode, with sec task etc)
    // console.log(parameter_dict);
    // delete app;
    if(parameter_dict['debug']==1){
         app = new MOT(parameter_dict['n_targets'],parameter_dict['n_distractors'],
              Math.round(ppd*parameter_dict['angle_max']), Math.round(ppd*parameter_dict['angle_min']),
              parameter_dict['radius'],parameter_dict['speed_max'], parameter_dict['speed_max']);
    }else{
        if(parameter_dict['gaming']==0){
            console.log("no gaming mode");
            app = new MOT_Game_Light(parameter_dict['n_targets'],parameter_dict['n_distractors'],
                Math.round(ppd*parameter_dict['angle_max']), Math.round(ppd*parameter_dict['angle_min']),
                parameter_dict['radius'],parameter_dict['speed_max'], parameter_dict['speed_max'], 'green', 'red');
        }else if(parameter_dict['gaming']==1){
            app = new MOT_Game(parameter_dict['n_targets'], parameter_dict['n_distractors'],
                Math.round(ppd*parameter_dict['angle_max']), Math.round(ppd*parameter_dict['angle_min']),
                parameter_dict['radius'],parameter_dict['speed_max'], parameter_dict['speed_max'], goblin_image, guard_image);
            if(parameter_dict['secondary_task']!='none'){
                sec_task = new Secondary_Task(leaf_image, parameter_dict['secondary_task'], parameter_dict['SRI_max']*1000,
                    parameter_dict['RSI']*1000, parameter_dict['tracking_time']*1000, parameter_dict['delta_orientation'],
                         app.all_objects)
            }
        }
    }
    app.change_target_color();
    // Init timer, do not forget to parse it to ms
    timer(app, 1000*parameter_dict['presentation_time'],
        1000*parameter_dict['fixation_time'],
        1000*parameter_dict['tracking_time'],
        1000*parameter_dict['probe_time']);
    if(parameter_dict['admin_pannel']){
        // Adjust pannel parameters to current parameter_dict:
        update_parameters_values();
        // Show hide-show parameters button:
        button_hide_params.show();
        // If current hidden variable is set to true, show inputs:
        if(!hidden_pannel){
            button_hide_params.elt.innerHTML = 'HIDE <<';
            button_hide_params.position(7*150/4, windowHeight - 2.8*step);
            show_inputs();
        }
    }
}
function show_answer_button(){
    button_answer.show();
}
function answer_button_clicked(){
    // reset few variables:
    fill_bar_size = 0;
    show_probe_timer = false;
    clearTimeout(probe_timer);
    button_answer.hide();
    let res = app.get_results();
    parameter_dict['nb_target_retrieved'] = res[0];
    parameter_dict['nb_distract_retrieved'] = res[1];
    if(parameter_dict['gaming']==1 && parameter_dict['secondary_task']!='none'){
        console.log("sec_task results", sec_task.results);
        parameter_dict['sec_task_results'] = JSON.stringify(sec_task.results);
    }
    app.phase = 'got_response';
    app.change_to_same_color();
    app.change_target_color();
    app.all_objects.forEach(function(item){item.interact_phase = false;});
    button_next_episode.show();
}
function next_episode(){
    // update score
    parameter_dict['score'] = parameter_dict['score']+(parameter_dict['nb_target_retrieved'] * 10) - ((app.n_distractors - parameter_dict['nb_distract_retrieved'])*10);
    if(parameter_dict['score'] < 0){parameter_dict['score']=0}
    console.log(parameter_dict['score']);
    // First set_up prompt of transition pannel:
    message = 'Vous avez retrouvé '+ parameter_dict['nb_target_retrieved'] + '/' + app.n_targets +' cibles.';
    let add_message = '\n Malheureusement, il en manque '+ str(app.n_targets- parameter_dict['nb_target_retrieved']) +'.';
    if(parameter_dict['nb_target_retrieved'] == app.n_targets){
        if(parameter_dict['nb_distract_retrieved'] == app.n_distractors){
            add_message = '\n Bien joué!';
        }else{
            var nb = str(app.n_distractors - parameter_dict['nb_distract_retrieved']);
            add_message = '\n Malheureusement, vous avez aussi sélectionné '+ nb +' guarde(s)! Évitez les la prochaine fois.';
        }
    }
    var final_message = '\n' + str(parameter_dict['episode_number']+1) + ' épisode(s) consécutif(s) joués. Continuez !';
    message = message + add_message + final_message;
    // Then prepare to next phase:
    button_next_episode.hide();
    // Send ajax request to backend:
    $.ajax({
    async: false,
    type: "POST",
    url: "/next_episode",
    dataType: "json",
    traditional: true,
    data: parameter_dict,
    success: function(data) {
        parameter_dict = data;
        }
    });
    paused = true;
    button_keep.show();
    if(parameter_dict['admin_pannel']){
        hide_inputs();
        button_hide_params.hide();
    }
}


