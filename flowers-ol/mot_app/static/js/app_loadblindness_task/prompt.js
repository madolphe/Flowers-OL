let prompt_start, prompt_question_direction, prompt_question_input, prompt_question_contrast, prompt_button_here,
prompt_gratitude, prompt_button_end, prompt_button_restart;
let text_title_0, text_tutorial_0_0, text_tutorial_0_1, text_tutorial_0_2, text_tutorial_0_3;
let text_tutorial_1_0, text_tutorial_2_0, text_tutorial_2_1, text_tutorial_2_2, text_tutorial_3_1,text_tutorial_3_2,
    text_tutorial_4_0, text_tutorial_5_0, text_tutorial_6_1, text_tutorial_6_2;
let text_start, text_end, text_fixation_answer1, text_fixation_answer2;
let text_button_next, text_button_previous, text_button_start, text_question_target, text_question_length;

if(language_code==='fr'){
    prompt_start = "Cliquez sur la souris pour débuter l'activité";
    prompt_question_direction = "Direction de la ligne la plus longue: verticale ou horizontale?";
    prompt_question_input = "Verticale: appuyer sur \"f\"     Horizontale: appuyer sur \"j\"";
    prompt_question_contrast = "Quelle cible était la plus contrastée ?";
    prompt_button_here = "Ici!";
    prompt_gratitude = "Merci d'avoir participé à l'expérience";
    prompt_button_end = "FIN";
    prompt_button_restart = "Redémarrer";
   // TUTORIAL
    text_title_0 = "INSTRUCTIONS" ;
    text_tutorial_0_0 = "Le but de cette expérience est de mesurer votre capacité d'attention" ;
    text_tutorial_0_1 = "à des cibles multiples. À chaque essai, vous verrez " ;
    text_tutorial_0_2 = "une brève présentation d'une cible en croix ainsi que quatre objets à rayures" ;
    text_tutorial_0_3 = "Vous devez compléter deux tâches pour chaque essai" ;
    text_tutorial_1_0 = "Ceci est un exemple de présentation de stimulus" ;
    text_tutorial_2_0 = "D'abord, vous devez répondre à la question : quelle ligne était la plus longue?" ;
    text_tutorial_2_1 = "Ensuite, vous devez répondre à la question: quel objet avait le plus fort contraste" ;
    text_tutorial_2_2 = "en cliquant sur l'un des quatre boutons" ;
    text_tutorial_3_0 = "Commencons les exercices.";
    text_tutorial_3_1 = "N'oubliez pas que vous devez répondre correctement" ;
    text_tutorial_3_2 = "au moins à la première question concernant la longueur des lignes" ;
    text_tutorial_4_0 = "Commençons l'expérience principale" ;
    text_tutorial_5_0 = "Temps de pause." ;
    text_tutorial_6_1 = "Merci pour votre effort. Lorsque vous êtes prêts, " ;
    text_tutorial_6_2 = "Veuillez cliquer sur le bouton de démarrage pour redémarrer." ;
    // TASK
    text_fixation_answer1 = "Horizontal" ;
    text_fixation_answer2 = "Vertical" ;
    text_start = "Veuillez cliquer sur la souris pour commencer cette expérience" ;
    text_end = "Merci de participer à l'expérience" ;
    text_button_next = "Suivant";
    text_button_previous = "Précédent";
    text_button_start = "Démarrer";
    text_question_target="Quelle cible était la plus contrastée?";
    text_question_length = "Quelle ligne était la plus longue?";

}else{
    prompt_start = "Please click the mouse to start this experiment";
    prompt_question_direction = "Which line was longer, vertical or horizontal?";
    prompt_question_input = "Vertical:press key \"f\"     Horizontal:press key\"j\"";
    prompt_question_contrast = "Which target contrast was strong?";
    prompt_button_here = "Here!";
    prompt_gratitude = "Thank you for joining the experiment.";
    prompt_button_end = "END";
    prompt_button_restart = "RESTART";
    // TUTORIAL
    text_title_0 = "INSTRUCTIONS";
    text_tutorial_0_0 = "The goal of this experiment is to measure your attention ability";
    text_tutorial_0_1 = "to multiple targets. On each trial, you will see";
    text_tutorial_0_2 = "a brief presentation of a cross target with four stripe objects.";
    text_tutorial_0_3 = "You have to answer two tasks for each trial.";
    text_tutorial_1_0 = "This is an example of stimulus presentation.";
    text_tutorial_2_0 = "First, you have to answer which of the lines was longer.";
    text_tutorial_2_1 = "Next, you have to answer which of the four objects had the strong contrast";
    text_tutorial_2_2 = "by clicking one of the four buttons.";
    text_tutorial_3_0 = "Let's start the practices.";
    text_tutorial_3_1 = "Please keep in mind that you have to correctly answer";
    text_tutorial_3_2 = "at least the first length question.";
    text_tutorial_4_0 = "Let's start the main experiment.";
    text_tutorial_5_0 = "Break time.";
    text_tutorial_6_1 = "Thank you for your effort. When you are ready,";
    text_tutorial_6_2 = "please click the start button to restart.";
    // TASK
    text_fixation_answer1 = "Horizontal";
    text_fixation_answer2 = "Vertical";
    text_start = "Please click the mouse to start this experiment";
    text_end = "Thank you for joining the experiment.";
    text_button_next = "Next";
    text_button_previous = "Previous";
    text_button_start = "Start";
    text_question_target="Which target contrast was strong?";
    text_question_length = "Which was longer?";
}