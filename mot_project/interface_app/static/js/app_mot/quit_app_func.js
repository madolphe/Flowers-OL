function display_exit(){
    width = 100;
    height = 45;
    push();
    button_exit.position(windowWidth-(width*1.3), 50 - (height/2));
    button_exit.size(width,height);
    button_exit.mousePressed(quit_game);

    button_pause.position(windowWidth-(width*1.3), 80 );
    button_pause.size(width, height);
    button_pause.mousePressed(quit_game);
    pop();
}
function quit_game(){
        // put here current results !
        post('home_user', parameter_dict, 'post')
}
