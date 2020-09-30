let bot_mode = true;
let bot_skill = 1;

function bot_answer(app){
    if(app.phase=='answer'){
        // Time for the bot to select an answer:
        // Bot always win:
        console.log("Select an answer once");
        if(Math.random()>1-bot_skill){
            app.targets.forEach(function(item){item.pressed=true});
        }else{
            app.targets.forEach(function(item){if(Math.random()>0.2){item.pressed=true}});
            app.distractors.forEach(function(item){if(Math.random()>0.8){item.pressed=true}});
        }
        app.phase = 'wait';
    }
    if(app.phase == 'got_response'){
        if(bot_skill<1){
            bot_skill *= 1.001;
        }
        console.log("before push next_episode button");
        next_episode();
        app.phase = 'fixation';
        setTimeout(function(){start_episode(); console.log("new episode launch")}, 1)
    }
}
