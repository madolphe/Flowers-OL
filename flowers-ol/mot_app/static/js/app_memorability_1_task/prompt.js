let prompt_start, prompt_gratitude , prompt_correct, prompt_wrong ,prompt_button_end, prompt_button_restart;
let text_title_0, text_tutorial_0_0, text_tutorial_0_1, text_tutorial_0_2, text_tutorial_0_3;
let text_tutorial_1_0,text_tutorial_1_1,text_tutorial_1_2, text_tutorial_2_0, text_tutorial_3_0, text_tutorial_4_0,
    text_tutorial_5_0, text_tutorial_6_1, text_tutorial_6_2;
let text_start, text_end;
let text_button_next, text_button_previous, text_button_start;

if(language_code==='fr'){
    prompt_start = "Cliquez sur la souris pour débuter l'activité";
    prompt_gratitude = "Merci d'avoir participé à l'expérience";
    prompt_correct = "Correct";
    prompt_wrong = "Incorrect";
    prompt_button_end = "END";
    prompt_button_restart = "Redémarrer";
  // Tâche
    text_start = "Veuillez cliquer sur la souris pour commencer cette expérience" ;
    text_end = "Merci de participer à l'expérience" ;
    // TUTORIAL
    text_title_0 = "INSTRUCTIONS" ;
    text_tutorial_0_0 = "Le but de cette expérience est de mesurer votre capacité de mémoire." ;
    text_tutorial_0_1 = "A chaque essai, vous verrez un ensemble de photographies une par une." ;
    text_tutorial_0_2 = "Votre tâche est de vous souvenir de chaque photographie et de répondre si " ;
    text_tutorial_0_3 = "la photographie est présentée deux fois ou non." ;
    text_tutorial_1_0 = "Certaines images apparaîtront deux fois, mais les autres une seule fois.";
    text_tutorial_1_1 = "Lorsque vous remarquez que l'image est présentée deux fois," ;
    text_tutorial_1_2 = "veuillez appuyer sur la touche [J] dès que possible" ;
    text_tutorial_2_0 = "A chaque essai, vous obtiendrez un retour d'information vous indiquant si votre réponse est correcte." ;
    text_tutorial_3_0 = "Commençons les essais." ;
    text_tutorial_4_0 = "Commençons l'expérience principale." ;
    text_tutorial_5_0 = "Temps de pause." ;
    text_tutorial_6_1 = "Merci pour votre effort. Lorsque vous êtes prêt," ;
    text_tutorial_6_2 = "veuillez cliquer sur le bouton de démarrage pour redémarrer" ;
    text_button_next = "Suivant";
    text_button_previous = "Précédent";
    text_button_start = "Démarrer";
}else{
    prompt_start = "Please click the mouse to start this experiment";
    prompt_gratitude = "Thank you for joining the experiment.";
    prompt_correct = "Correct Answer";
    prompt_wrong = "Wrong Answer";
    prompt_button_end = "END";
    prompt_button_restart = "RESTART";
    // Task
    text_start = "Please click the mouse to start this experiment";
    text_end = "Thank you for joining the experiment.";
    // TUTORIAL
    text_title_0 = "INSTRUCTIONS";
    text_tutorial_0_0 = "The goal of this experiment is to measure your memory capacity.";
    text_tutorial_0_1 = "On each trial, you will see a set of photographs one-by-one.";
    text_tutorial_0_2 = "Your task is to remember each photograph and answer whether ";
    text_tutorial_0_3 = "the photograph is presented twice or not.";
    text_tutorial_1_0 = "Some images will appear twice, but the others just once.";
    text_tutorial_1_1 = "When you notice the image is presented twice,";
    text_tutorial_1_2 = "please press the key [J] on your keyboard as soon as possible.";
    text_tutorial_6_1 = "Thank you for your effort. When you are ready,";
    text_tutorial_6_2 = "please click the start button to restart.";
    text_tutorial_2_0 = "On each trial, you will get feedback about if your response is correct.";
    text_tutorial_3_0 = "Let's start the practices.";
    text_tutorial_4_0 = "Let's start the main experiment.";
    text_tutorial_5_0 = "Break time.";
    text_button_next = "Next";
    text_button_previous = "Previous";
    text_button_start = "Start";
}