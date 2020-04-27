let cross_length = 10;
let radius;

// main function used to display :
function play(disp_zone){
    display_fixation_cross(cross_length);
    if(disp_zone){
        display_game_zone(3, 9);
    }
    app.display_objects(mouseX, mouseY);
    app.check_collisions();
    app.move_objects();
    sec_task.display_task();
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
    stroke('red');
    strokeWeight(2);
    line((windowWidth/2)-cross_length,windowHeight/2, (windowWidth/2)+cross_length, windowHeight/2);
    line(windowWidth/2,(windowHeight/2)-cross_length, windowWidth/2, (windowHeight/2)+cross_length);
    pop();
}

function start_episode(){
    if(parameter_dict['episode_number']<8){
        //app = new MOT(3,3, Math.round(ppd*9), Math.round(ppd*3), 70, 2, 2);
        console.log('init app');
        if(parameter_dict['debug']==1){
             app = new MOT(parameter_dict['n_targets'], parameter_dict['n_distractors'], Math.round(ppd*parameter_dict['angle_max']),
                  Math.round(ppd*parameter_dict['angle_min']), parameter_dict['radius'],parameter_dict['speed_min'],
                  parameter_dict['speed_max']);
        }else{
             app = new MOT_Game(parameter_dict['n_targets'], parameter_dict['n_distractors'], Math.round(ppd*parameter_dict['angle_max']),
                  Math.round(ppd*parameter_dict['angle_min']), parameter_dict['radius'],parameter_dict['speed_min'],
                  parameter_dict['speed_max'], goblin_image, guard_image);
        }
        if(parameter_dict['secondary_task']!='none'){
            sec_task = new Secondary_Task(leaf_image, 'discrimination', 2000, 1000, parameter_dict['tracking_time'],
                70, app.all_objects)
        }
        app.change_target_color();
        // timer(app, 2000, 2000, 10000);
        timer(app, parameter_dict['presentation_time'],
            parameter_dict['fixation_time'],
            parameter_dict['tracking_time']);
    }else{
        quit_game();
    }
}

function timer(app, presentation_time, fixation_time, tracking_time){
    setTimeout(function () {
        // after presention_time ms
        // app.phase changes to fixation
        app.phase = 'fixation';
        app.frozen = true;
        // and stay in this frozen mode for fixation_time ms
        setTimeout(function(){
            // after fixation_time ms
            // app.phase change to tracking mode
            sec_task.timer_pause();
            app.phase = 'tracking';
            app.frozen = false;
            app.change_to_same_color();
            // and stay in this mode for tracking_time ms
            setTimeout(function(){
                // after tracking_time ms, app changes to answer phase
                app.phase = 'answer';
                app.frozen = true;
                app.enable_interact();
                show_answer_button(); },
                tracking_time)},
            fixation_time)
    }, presentation_time);
}

function show_answer_button(){
    button_answer = createButton('ANSWER');
    button_answer.position((windowWidth/2)-60, windowHeight - 0.07*windowHeight);
    button_answer.size(120,60);
    button_answer.mousePressed(answer_button_clicked);
}

function answer_button_clicked(){
    button_answer.hide();
    let res = app.get_results();
    parameter_dict['nb_target_retrieved'] = res[0];
    parameter_dict['nb_distract_retrieved'] = res[1];
    app.phase = 'got_response';
    app.change_to_same_color();
    app.change_target_color();
    app.all_objects.forEach(function(item){item.interact_phase = false;});
    button_next_episode = createButton('NEXT EPISODE');
    button_next_episode.position((windowWidth/2)-60, windowHeight - 0.07*windowHeight);
    button_next_episode.size(120,60);
    button_next_episode.mousePressed(next_episode);
}

function next_episode(){
    //console.log(parameter_dict);
    button_next_episode.hide();
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
    start_episode();
}


