function start_mode(){
    width = 170;
    height = 70;
    push();
    fill(hover_color);
    // rect(windowWidth/2, windowHeight/2 - 50, 170, 70);
    // rect(windowWidth/2, windowHeight/2 + 50, 170, 70);
    rectMode(CENTER);
    rect(windowWidth/2, windowHeight/2, windowWidth, 500);

    button_play.position(windowWidth/2-(width/2), windowHeight/2 - 50 - (height/2));
    button_play.size(width,height);
    button_play.mousePressed(launch_app);

    button_tuto.position(windowWidth/2-(width/2), windowHeight/2 + 50 - (height/2));
    button_tuto.size(width,height);
    button_tuto.mousePressed(launch_tuto);
    // to remove:
    add_hover(windowWidth/2, windowHeight/2 - 50, width/2, height/2);
    add_hover(windowWidth/2, windowHeight/2 + 50, width/2, height/2);
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
    mode = 'play';
    button_play.hide();
    button_tuto.hide();
    fullscreen(true);
    set_screen_params();
    start_episode();
}
function launch_tuto(){
    mode = 'tuto';
    button_play.hide();
    button_tuto.hide();
}

