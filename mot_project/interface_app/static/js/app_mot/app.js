// p5.js functions to display the game:
function preload() {
    arena_background = loadImage('/static/images/bavelier_lab/arena.png');
    guard_image = loadImage('/static/images/bavelier_lab/guard.png');
    goblin_image = loadImage('/static/images/bavelier_lab/goblin.png');
    leaf_image = loadImage('/static/images/bavelier_lab/leaf.png');
    timer_image = loadImage('static/images/timer.png');
}
function setup(){
    gill_font_light = loadFont('/static/font/gillsansstd/GillSansStd-Light.otf');
    gill_font = loadFont('/static/font/gillsansstd/GillSansStd.otf');
    frameRate(60);
    mode = 'start';
    hover_color = color(255, 255, 255);
    hover_color.setAlpha(150);
    canvas = createCanvas(windowWidth, windowHeight);
    canvas.parent('app_holder');
    button_play = createButton('PLAY');
    button_tuto = createButton('TUTO');
    button_exit = createButton('EXIT');
    button_pause = createButton('PAUSE');
    button_keep = createButton('PLAY');
    button_keep.hide();
    button_tuto.hide();
    button_pause.hide();
    textAlign(CENTER, CENTER);
}
function draw(){
    push();
    background(0);
    if(parameter_dict['gaming']==1){
        imageMode(CENTER);
        image(arena_background, windowWidth/2, windowHeight/2);
    }
    //always display exit button:
    display_exit();
    if(mode=='start'){
        start_mode();
    }else if (mode =='play') {
        time_step ++;
        if(time_step % 60 == 0){
            time_step = 0;
            game_time --;
        }
        play(parameter_dict['debug']);
    }
    pop();
}
function mousePressed(event) {
    if((mouseX > canvas.width-40)&&(mouseY<40)){quit_game()}
    console.log(mouseX, mouseY);//console.log(canvas.width);
   // First test if objects are in "clickable mode"
   //if (app.distractors[0].hover) {
    if(app.phase=='answer'){
        app.check_mouse_pressed(mouseX, mouseY);
    }
   //}
}
function windowResized(){
      canvas = createCanvas(windowWidth, windowHeight);
      position_inputs();
      size_inputs();
}

function keyPressed(){
    if(sec_task instanceof Secondary_Task){
        sec_task.keyboard_pressed(keyCode);
    }
}

function mouseReleased() {
    update_input_from_slider_value();
    console.log('app');
}

