// Variables needed for object in canvas:
let window_width;
let window_height;
let canvas;
let hover_color;
let app;
let delta = 0; // camera angle for answering phase
let back = false; // variable used by camera to get back to initial position
let answer_phase = false;
let background_img;
let shark_img;
let fish_left_img;
let fish_right_img;
let img_width, img_height;
let parameter_dict = {};
let results = {};
let numbers = [];
let exit;
// clear session storage:
sessionStorage.clear();

// p5.js functions to display the game:
function preload() {
  // Load model with normalise parameter set to true
    // background_img = loadImage('/static/images/starBackground.png');
    // background_img = loadImage('/static/images/ggj/krakee.png');
    //shark_img = loadImage('/static/images/ggj/shark1.png');
    // fish_left_img = loadImage('/static/images/ggj/f1_left.png');
    // fish_right_img = loadImage('/static/images/ggj/f1_right.png');
}
function setup(){
    let i;
    for(i = 1; i<9; i++){
        path = '/static/images/kenney_fishPack/PNG/Retina/'+str(i)+'.png';
        numbers.push(loadImage(path))
    }
    exit = loadImage('/static/images/kenney_fishPack/PNG/Retina/exit.png');
    numbers.push(loadImage('/static/images/kenney_fishPack/PNG/Retina/double_point.png'));
    background_img = loadImage('/static/images/ggj/krakee.png');
    fish_left_img = loadImage('/static/images/ggj/f1_left.png');
    fish_right_img = loadImage('/static/images/ggj/f1_right.png');
    console.log(fish_right_img, fish_left_img);
    img_width = fish_left_img.width;
    img_height = fish_left_img.height;
    window_height = 0.6*windowHeight;
    window_width = 0.6*windowWidth;
    canvas = createCanvas(window_width, window_height);
    canvas.parent('app_holder');
    hover_color = color(255, 255, 255);
    hover_color.setAlpha(200);
    start_episode();
}
function draw(){
    // background(100);
    background(background_img);
    noFill();
    if(app.phase=='fixation'||app.phase == 'got_response'){app.change_to_initial_color()}
    app.display_balls(mouseX, mouseY);
    app.check_collisions();
    app.move_balls();
    push();
    scale(0.4);
    image(numbers[parameter_dict['episode_number']], 0, 0);
    image(numbers[7], 110, 0);
    image(numbers[8], 50, 0);
    pop();
    push();
    imageMode(CENTER);
    // scale(0.9);
    image(exit, canvas.width-35, 35, exit.width*0.85, exit.height*0.85);
    pop();
}
function mousePressed(event) {
    if((mouseX > canvas.width-40)&&(mouseY<40)){quit_game()}
    console.log(mouseX, mouseY);
    console.log(canvas.width);
   // First test if objects are in "clickable mode"
   if (app.distractors[0].hover) {
       app.check_mouse_pressed(mouseX, mouseY);
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
function windowResized(){
      createCanvas(0.9*windowWidth, 0.9*windowHeight);
}

// Additional functions to interract with user:
function start_episode(){
    if(parameter_dict['episode_number']<8){
        app = new Space_App(parameter_dict['n_targets'], parameter_dict['n_distractors'],
                    parameter_dict['target_color'], parameter_dict['distractor_color'],
                    window_width, window_height, parameter_dict['radius_min'], parameter_dict['radius_max'],
                    parameter_dict['speed_min'], parameter_dict['speed_max'], hover_color, fish_left_img,
                    fish_right_img, img_width, img_height);
        app.change_to_same_color();
        // check whether the timer could be incorporate to app!
        timer(app, 2000, 2000, 5000);
    }else{
        quit_game();
    }
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
function quit_game(){
        // put here current results !
        post('home_user', parameter_dict, 'post')
}
function post(path, params, method='post') {
    // Function to ask for parameters of new episode
    // first create an hidden form:
    let form = document.getElementById('request');
    form.method = method;
    form.action = path;
    // Pass all parameters needed:
    for (const key in params) {
        if (params.hasOwnProperty(key)) {
          const hiddenField = document.createElement('input');
          hiddenField.type = 'hidden';
          hiddenField.name = key;
          hiddenField.value = params[key];
          form.appendChild(hiddenField)}
    }
    document.body.appendChild(form);
    form.submit();
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