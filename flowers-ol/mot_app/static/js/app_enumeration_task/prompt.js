let prompt_start, prompt_question , prompt_gratitude, prompt_button_restart;
let text_title_0, text_tutorial_0_0, text_tutorial_0_1, text_tutorial_0_2, text_tutorial_0_3;
let text_tutorial_1_0, text_tutorial_1_1, text_tutorial_1_2, text_tutorial_2_0, text_tutorial_2_1, text_tutorial_2_2,
    text_tutorial_4_0, text_tutorial_5_0, text_tutorial_6_1, text_tutorial_6_2;
let text_1left , text_1right,text_2left,text_2right,text_start, text_end;

if(language_code==='fr'){
    prompt_start = "Cliquez sur la souris pour débuter l'activité";
    prompt_question = "Combien de cercles avez-vous vu?";
    prompt_gratitude = "Merci d'avoir participé à l'expérience";
    prompt_button_restart = "Redémarrer";
    // CONFIG :
    text_start = "Veuillez cliquer sur la souris pour commencer cette expérience" ;
    text_end = "Merci de participer à l'expérience" ;
    // TUTORIAL :
    text_title_0 = "INSTRUCTIONS" ;
    text_tutorial_0_0 = "Le but de cette expérience est de mesurer votre capacité à compter" ;
    text_tutorial_0_1 = "A chaque essai, vous verrez un bref flash de plusieurs cercles blancs" ;
    text_tutorial_0_2 = "Votre tâche est de compter ces cercles et de répondre combien de cercles" ;
    text_tutorial_0_3 = "ont été présentés à l'aide d'un selecteur coulissant" ;
    text_tutorial_1_0 = "Souviens-toi du nombre de ces cercles blancs" ;
    text_tutorial_2_0 = "Veuillez répondre au nombre de cercles présentés à l'aide du selecteur coulissante" ;
    text_tutorial_3_0 = "Pratiquons un peu" ;
    //scène principale prête
    text_tutorial_4_0 = "Commençons l'expérience principale." ; //scene main ready
    //scène pause
    text_tutorial_5_0 = "Temps de pause." ;
    text_tutorial_6_1 = "Merci pour votre effort. Lorsque vous êtes prêt," ;
    text_tutorial_6_2 = "Veuillez cliquer sur le bouton de démarrage pour redémarrer" ;
}else{
    prompt_start = "Please click the mouse to start this experiment";
    prompt_question = "How many circles are presented?";
    prompt_gratitude = "Thank you for joining the experiment.";
    prompt_button_restart = "RESTART";
    // CONFIG:
    text_start = "Please click the mouse to start this experiment";
    text_end = "Thank you for joining the experiment.";
    // TUTORIAL:
    text_title_0 = "INSTRUCTIONS";
    text_tutorial_0_0 = "The goal of this experiment is to measure your counting ability.";
    text_tutorial_0_1 = "On each trial, you will see a brief flash of multiple white circles.";
    text_tutorial_0_2 = "Your task is to count these circles and answer how many circles";
    text_tutorial_0_3 = "were presented using a slider bar.";
    text_tutorial_1_0 = "Please remember the number of these white circles.";
    text_tutorial_2_0 = "Please answer how many circles were presented using a slider bar";
    text_tutorial_3_0 = "Let's start the practices.";
    //scene main ready
    text_tutorial_4_0 = "Let's start the main experiment.";
    //scene break
    text_tutorial_5_0 = "Break time.";
    text_tutorial_6_1 = "Thank you for your effort. When you are ready,";
    text_tutorial_6_2 = "please click the start button to restart.";
}