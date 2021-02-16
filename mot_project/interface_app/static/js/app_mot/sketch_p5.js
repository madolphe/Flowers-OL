// p5.js functions to display the game:
function preload() {
    arena_background_init = loadImage('/static/images/bavelier_lab/arena.png',
        img => {arena_background = img.get()});
    // arena_background_init = loadImage('/static/images/bavelier_lab/arena.png');
    guard_image = loadImage('/static/images/bavelier_lab/guard.png');
    goblin_image = loadImage('/static/images/bavelier_lab/goblin.png');
    leaf_image = loadImage('/static/images/bavelier_lab/leaf.png');
    timer_image = loadImage('static/images/timer.png');
}
function setup(){
    let button_exit_width = windowWidth/20;
    let button_exit_height = windowHeight/20;
    let button_height = 60;
    let button_width = 120;

    set_screen_params();
    radius = Math.round(ppd*max_angle);

    gill_font_light = loadFont('/static/font/gillsansstd/GillSansStd-Light.otf');
    gill_font = loadFont('/static/font/gillsansstd/GillSansStd.otf');
    frameRate(fps);
    mode = 'start';
    hover_color = color(255, 255, 255);
    hover_color.setAlpha(150);


    canvas = createCanvas(windowWidth, windowHeight);
    canvas.parent('app_holder');
    canvas.style('position: absolute; z-index: -1000;');

    // Creer methode
    button_answer = createButton('REPONSE');
    button_answer.position((windowWidth/2)-60, windowHeight - 0.07*windowHeight);
    button_answer.size(120,60);
    button_answer.mousePressed(answer_button_clicked);
    button_answer.hide();


    button_play = createButton('DEMARRER');
    button_play.position(windowWidth/2-(button_width/2), windowHeight/2  - (button_height/2));
    button_play.size(button_width,button_height);
    button_play.mousePressed(launch_app);
    button_play.hide();

    button_exit = createButton('SORTIE');
    button_exit.position(windowWidth-(100*1.3), 50 - (45/2));
    button_exit.size(button_exit_width,button_exit_height);
    button_exit.mousePressed(quit_game);

    button_pause = createButton('PAUSE');
    button_pause.hide();

    button_tuto = createButton('TUTO');
    button_tuto.hide();


    button_next_episode = createButton('EPISODE SUIVANT');
    button_next_episode.position((windowWidth/2)-60, windowHeight - 0.07*windowHeight);
    button_next_episode.size(button_width,button_height);
    button_next_episode.hide();
    button_next_episode.mousePressed(next_episode);


    button_keep = createButton('JOUER');
    button_keep.hide();
    button_keep.position(windowWidth/2 - button_width/2, windowHeight/2 + windowHeight/9);
    button_keep.size(button_width, button_height);
    button_keep.mousePressed(start_episode);

    textAlign(CENTER, CENTER);
}
function draw(){
    push();
    background(0);
    arena_background.resize(1.1*radius,0);
    if(parameter_dict['gaming']==1){
        imageMode(CENTER);
        image(arena_background, windowWidth/2, windowHeight/2);
    }
    if(mode=='start'){
        start_mode();
    }else if (mode =='play') {
        if(frameCount % fps == 0){
            game_time --;
        }
        play(parameter_dict['debug']);
    }
    pop();
}
function mousePressed(event) {
    if((mouseX > canvas.width-40)&&(mouseY<40)){quit_game()}
   // First test if objects are in "clickable mode"
    if (typeof app !== 'undefined') {
        if(app.phase=='answer'){
            app.check_mouse_pressed(mouseX, mouseY);
        }
    }
}
function windowResized(){
    canvas = createCanvas(windowWidth, windowHeight);
    if(parameter_dict['admin_pannel']){
    position_inputs();
    size_inputs();
    }
    // nommer tous les coefficients
    // Pq toutes ces formules ? --> variable explicite
    // ex: heightCenter = windowWidth / 2 same heightCenter
    button_next_episode.position((windowWidth/2)-60, windowHeight - 0.07*windowHeight);
    button_answer.position((windowWidth/2)-60, windowHeight - 0.07*windowHeight);
    button_play.position(windowWidth/2-(button_width/2), windowHeight/2  - (button_height/2));
    button_exit.position(windowWidth-(100*1.3), 50 - (45/2));
    button_keep.position(windowWidth/2 - button_width/2, windowHeight/2 + windowHeight/9);
    set_screen_params();
}

function keyPressed(){
    if(sec_task instanceof Secondary_Task){
        sec_task.keyboard_pressed(keyCode);
    }
}

function mouseReleased() {
    update_input_from_slider_value();
}


