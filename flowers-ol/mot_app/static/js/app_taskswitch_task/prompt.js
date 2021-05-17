let prompt_start, prompt_gratitude, prompt_button_end, prompt_button_restart;
let text_title_0, text_tutorial_0_0, text_tutorial_0_1, text_tutorial_0_2, text_tutorial_0_3;
let text_tutorial_1_0, text_tutorial_1_1, text_tutorial_1_2, text_tutorial_2_0, text_tutorial_2_1, text_tutorial_2_2,
    text_tutorial_4_0, text_tutorial_5_0, text_tutorial_6_1, text_tutorial_6_2;
let text_1left , text_1right,text_2left,text_2right,text_start, text_end;
let text_button_next, text_button_previous, text_button_start;

if(language_code==='fr'){
    prompt_start = "Cliquez sur la souris pour débuter l'activité";
    prompt_gratitude = "Merci d'avoir participé à l'expérience";
    prompt_button_end = "FIN";
    prompt_button_restart = "Redémarrer";
    text_title_0 = "INSTRUCTIONS";
    text_tutorial_0_0 = "Le but de cette expérience est de mesurer votre capacité " ;
    text_tutorial_0_1 = "à orienter votre attention. A chaque essai, vous verrez un chiffre " ;
    text_tutorial_0_2 = "de l'ensemble {1-4, 6-9} sur un fond rouge ou bleu" ;
    text_tutorial_0_3 = "Vos tâches changeront avec le fond d'écran comme suit" ;
    text_tutorial_1_0 = "Lorsque le repère est le fond bleu en forme de losange," ;
    text_tutorial_1_1 = "vous devez répondre si le chiffre cible est pair ou impair" ;
    text_tutorial_1_2 = "en utilisant la touche [F] ou [J], respectivement" ;
    text_tutorial_2_0 = "Lorsque l'indice est le fond carré rouge, vous devez" ;
    text_tutorial_2_1 = "répondre si le chiffre cible est inférieur ou supérieur à 5" ;
    text_tutorial_2_2 = "en utilisant la touche [F] ou [J], respectivement" ;
    text_tutorial_4_0 = "Commençons l'expérience principale" ;
    text_tutorial_5_0 = "Temps de pause." ;
    text_tutorial_6_1 = "Merci pour votre effort. Lorsque vous êtes prêts, " ;
    text_tutorial_6_2 = "veuillez cliquer sur le bouton de démarrage pour redémarrer" ;
    text_1left = "Impair" ;
    text_1right = "Pair" ;
    text_2left = "Inférieur" ;
    text_2right = "Supérieur" ;
    text_start = "Veuillez cliquer sur la souris pour commencer cette expérience" ;
    text_end = "Merci d'avoir participer à l'expérience" ;
    text_button_next = "Suivant";
    text_button_previous = "Précédent";
    text_button_start = "Démarrer";
}else{
    prompt_start = "Please click the mouse to start this experiment";
    prompt_gratitude = "Thank you for joining the experiment.";
    prompt_button_end = "END";
    prompt_button_restart = "RESTART";
    // TUTORIAL:
    text_title_0 = "INSTRUCTIONS";
    text_tutorial_0_0 = "The goal of this experiment is to measure the ability ";
    text_tutorial_0_1 = "to switch your attention. On each trial, you will see a digit ";
    text_tutorial_0_2 = "from the set {1– 4, 6–9} on the cue background of red or blue.";
    text_tutorial_0_3 = "Your tasks will change with the cue background as follows.";
    text_tutorial_1_0 = "When the cue is the blue diamond-shaped background,";
    text_tutorial_1_1 = "you have to answer whether the target digit is odd or even";
    text_tutorial_1_2 = "by using the key [F] or [J] on your keyboard, respectively.";
    text_tutorial_2_0 = "When the cue is the red square background, you have";
    text_tutorial_2_1 = "to answer whether the target digit is lower or higher than 5";
    text_tutorial_2_2 = "by using the key [F] or [J], respectively.";
    text_tutorial_4_0 = "Let's start the main experiment.";
    text_tutorial_5_0 = "Break time.";
    text_tutorial_6_1 = "Thank you for your effort. When you are ready,";
    text_tutorial_6_2 = "please click the start button to restart.";
    // TASK:
    text_1left = "Odd";
    text_1right = "Even";
    text_2left = "Low";
    text_2right = "High";
    text_start = "Please click the mouse to start this experiment";
    text_end = "Thank you for joining the experiment.";
    text_button_next = "Next";
    text_button_previous = "Previous";
    text_button_start = "Start";
}
