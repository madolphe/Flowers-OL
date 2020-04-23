// @TODO: add pannel to confirm exit (see text display)
// @TODO: add pannel to play game when paused
// @TODO: add css - hover on buttons
// @TODO: play mode
// @TODO: add admin panel

// p5.js functions to display the game:
function preload() {
    arena_background = loadImage('/static/images/bavelier_lab/arena.png');
    guard_image = loadImage('/static/images/bavelier_lab/guard.png');
    goblin_image = loadImage('/static/images/bavelier_lab/goblin.png');
    leaf_image = loadImage('/static/images/bavelier_lab/leaf.png');
}
function setup(){
    mode = 'start';
    hover_color = color(255, 255, 255);
    hover_color.setAlpha(150);
    canvas = createCanvas(windowWidth, windowHeight);
    canvas.parent('app_holder');
    button_play = createButton('PLAY');
    button_tuto = createButton('TUTO');
    button_exit = createButton('EXIT');
    button_pause = createButton('PAUSE');
    textAlign(CENTER, CENTER);
}
function draw(){
    push();
    background(0);
    imageMode(CENTER);
    image(arena_background, windowWidth/2, windowHeight/2);
    display_exit();
    if(mode=='start'){
        start_mode();
    }else if (mode =='play') {
        play(false);
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
}


