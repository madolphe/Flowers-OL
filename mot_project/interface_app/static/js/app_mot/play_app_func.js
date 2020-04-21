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
    update_episode_number();
    if(parameter_dict['episode_number']<8){
        app = new MOT(3,3, Math.round(ppd*9), Math.round(ppd*3), 70, 2, 2);
        console.log('init app');
        //app = new MOT(parameter_dict['n_targets'], parameter_dict['n_distractors'],
        //            parameter_dict['target_color'], parameter_dict['distractor_color'],
        //            500, 0, parameter_dict['radius_min'], parameter_dict['radius_max'],
        //            parameter_dict['speed_min'], parameter_dict['speed_max'], hover_color, fish_left_img,
        //            fish_right_img, img_width, img_height);
        console.log(app);
        // app.change_to_same_color();
        // check whether the timer could be incorporate to app!
        timer(app, 2000, 2000, 1000000);
    }else{
        quit_game();
    }
}

function timer(app, fixation_time, tracking_time, answer_time){
    setTimeout(function () {
        app.phase = 'fixation';
        app.frozen = true;
        setTimeout(function(){
            app.phase = 'tracking';
            app.frozen = false;
            app.change_to_same_color();
            setTimeout(function(){
                app.phase = 'answer';
                app.frozen = true;
                app.enable_hover();
                show_answer_button();
                },answer_time)
        }, tracking_time)
    }, fixation_time);
}

function show_answer_button(){
    document.getElementById("button_app").type = 'submit';
    document.getElementById("button_quit").classList.remove('offset-md-4');
}

function answer_button_clicked(){
    if(document.getElementById("button_app").value == 'Next_episode' ){
        document.getElementById("button_app").type = 'hidden';
        document.getElementById("button_app").value = 'Answer';
        document.getElementById("button_quit").classList.add('offset-md-8');
        next_episode();
    }
    else{
        results = app.get_results();
        parameter_dict['nb_target_retrieved'] = results[0];
        parameter_dict['nb_distract_retrieved'] = results[1];
        if(document.getElementById("button_app").value == 'Answer' ){
            console.log("clicked");
            app.phase = 'got_response';
            app.frozen = true;
            document.getElementById("button_app").value = 'Next_episode';
        }
    }
}

function next_episode(){
    //console.log(parameter_dict);
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

function update_episode_number(){
    //document.getElementById("episode_number").innerHTML = parameter_dict['episode_number'];
}


