
// scene 6
function scene_tutorial1(){
    //Title
    push();
    fill(col_titletext);
    textSize(size_titletext);
    textAlign(CENTER);
    text( text_title_0, pos_title_x, pos_title_y);
    pop();

    push();
    fill(col_tutorialtext);
    textSize(size_tutorialtext);
    textAlign(CENTER);
    text( text_tutorial_0_0, pos_tutorialtext_x, pos_tutorialtext_y);
    text( text_tutorial_0_1, pos_tutorialtext_x, pos_tutorialtext_y+shift_text);
    text( text_tutorial_0_2, pos_tutorialtext_x, pos_tutorialtext_y+2*shift_text);
    text( text_tutorial_0_3, pos_tutorialtext_x, pos_tutorialtext_y+3*shift_text);
    pop();
    //button
    button_next.mousePressed(()=>{
        button_previous.show();
        Time.update_tutorial_next();    
        });
}

function create_next_button(){
    button_next = createButton('Next');
    button_next.size(size_next_w,size_next_h);
    button_next.style('font-size', size_next_text + 'px');
    button_next.position(x_next, y_next);
    button_next.hide();
}

function create_previous_button(){
    button_previous = createButton('Previous');
    button_previous.size(size_previous_w,size_previous_h);
    button_previous.style('font-size', size_previous_text + 'px');
    button_previous.position(x_previous, y_previous);
    button_previous.hide();
}


// scene 7
function scene_tutorial2(){
    //image
    demo_img0();
    //text
    push();
    fill(col_tutorialtext);
    textSize(size_tutorialtext);
    textAlign(CENTER);
    text( text_tutorial_1_0, pos_tutorialtext_x1, pos_tutorialtext_y1);
    text( text_tutorial_1_1, pos_tutorialtext_x1, pos_tutorialtext_y1+shift_text);
    pop();

    //buttons
    button_next.mousePressed(()=>{
        Time.update_tutorial_next();    
        });
    button_previous.mousePressed(()=>{
        button_previous.hide();
        Time.update_tutorial_previous();    
        });
}

function demo_img0(){
    //1 second flickering
    let tmp_time = Time.starttime_block - Math.round(Date.now()/1000);
    push();
    fill(col_target);
    textSize(size_target);
    noStroke();
    textAlign(CENTER);
    if (tmp_time%2==0){
        text("3", Pos.center_x, (Pos.center_y)+(size_target/2));
    }else {
        text("7", Pos.center_x, (Pos.center_y)+(size_target/2));
    }
    pop();
}

// scene 8
function scene_tutorial3(){
    //image
    demo_img1();
    //text
    push();
    fill(col_tutorialtext);
    textSize(size_tutorialtext);
    textAlign(CENTER);
    text( text_tutorial_2_0, pos_tutorialtext_x2, pos_tutorialtext_y2);
    pop();


    //buttons
    button_next.mousePressed(()=>{
        button_next.hide();
        button_start.show();
        Time.update_tutorial_next();    
        });
    button_previous.mousePressed(()=>{
        Time.update_tutorial_previous();    
        });
}

function demo_img1(){
    //1 second flickering
    let tmp_time = Time.starttime_block - Math.round(Date.now()/1000);
    push();
    fill(col_target);
    textSize(size_target);
    noStroke();
    textAlign(CENTER);
    if (tmp_time%2==0){
        text("5", Pos.center_x, (Pos.center_y)+(size_target/2));
    }else {
        text("7", Pos.center_x, (Pos.center_y)+(size_target/2));
    }
    pop();
}

// scene 9
function scene_tutorial4(){

    //text
    push();
    fill(col_tutorialtext);
    textSize(size_tutorialtext3);
    textAlign(CENTER);
    text(text_tutorial_3_0, pos_tutorialtext_x3, pos_tutorialtext_y3);
    pop();

    push();
    fill(col_tutorialtext);
    textSize(size_tutorialtext);
    textAlign(CENTER);
    text( text_tutorial_3_1, pos_tutorialtext_x, pos_tutorialtext_y);
    pop();


    //buttons
    button_previous.mousePressed(()=>{
        button_next.show();
        button_start.hide();
        Time.update_tutorial_previous();    
        });
    button_start.mousePressed(()=>{
        button_previous.hide();
        button_start.hide();
        Params.num_rep = num_rep_practice;
        Params.time_stimduration = time_stimduration_practice;
        Time.start();    
        });    
}

function create_start_button(){
    button_start = createButton('Start');
    button_start.size(size_start_w,size_start_h);
    button_start.style('font-size', size_start_text + 'px');
    button_start.position(x_start, y_start);
    button_start.hide();
}

function scene_tutorial5(){
    //text
    push();
    fill(col_tutorialtext);
    textSize(size_tutorialtext3);
    textAlign(CENTER);
    text(text_tutorial_4_0, pos_tutorialtext_x3, pos_tutorialtext_y3);
    pop();

    push();
    fill(col_tutorialtext);
    textSize(size_tutorialtext);
    textAlign(CENTER);
    text( text_tutorial_4_1, pos_tutorialtext_x, pos_tutorialtext_y);
    pop();

    //buttons
    button_start.mousePressed(()=>{
        button_start.hide();
        Params = new ParameterManager();
        Params.num_rep = num_rep_main;
        Params.time_stimduration = time_stimduration_main;
        flag_practice = true;
        flag_break = true;
        Time.start();    
        });    
}

function scene_break(){
    //text
    push();
    fill(col_tutorialtext);
    textSize(size_tutorialtext3);
    textAlign(CENTER);
    text(text_tutorial_5_0, pos_tutorialtext_x3, pos_tutorialtext_y3);
    pop();

    //buttons
    button_start.mousePressed(()=>{
        button_start.hide();
        Params = new ParameterManager();
        Params.num_rep = num_rep_main;
        Params.time_stimduration = time_stimduration_main;
        flag_practice = false;
        count_break ++;
        if (count_break==max_break-1){
            flag_break = false;
        }else{
            flag_break = true;
        }
        Time.start();    
        });    
}