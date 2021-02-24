function start_mode(){
    let width = 170;
    let height = 70;
    button_play.show();
    push();
    fill(hover_color);
    rectMode(CENTER);
    rect(windowWidth/2, windowHeight/2, windowWidth, 500);
    // to remove:
    add_hover(windowWidth/2, windowHeight/2, width/2, height/2);
    add_hover(windowWidth/2, windowHeight/2, width/2, height/2);
    pop();
}
function add_hover(x, y, width, length){
    // SHOULD BE DONE WITH CSS!!!
    // add hover effect when it's needed:
    if (mouseX>(x-width)&&(mouseX<(x+width))){
        if((mouseY>(y-length)&&(mouseY<y+length))){
            push();
            rectMode(CENTER);
            rect(x, y, width*2.2, length*2.3);
            pop();
        }
    }
}
function launch_app(){
    time_step = 0;
    game_time = parameter_dict['game_time'];
    mode = 'play';
    button_play.hide();
    button_tuto.hide();
    fullscreen(true);
    // Add admin pannel if participant.study is zpdes-admin:
    if(parameter_dict['admin_pannel']){
        init_pannel();
    }
    set_screen_params();
    timer_end_game();
    start_episode();
}
function launch_tuto(){
    mode = 'tuto';
    button_play.hide();
    button_tuto.hide();
}

