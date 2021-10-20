// Screen params:
let diagcm;
//let diagcm = 39.116;
let res = 16/10;
let viewer_dist = 50;
// All params will be set up thx 2 "set_screen_params";
// size of diag, width, height in pixels:
let diagpx, screen_width_px, screen_height_px;
// size of screen in cm:
let screen_height, screen_width;
// nbr of pixels per cm:
let pixpcm;
// cm per deg:
let cmpd;
// pixels per deg:
let ppd;

// framerate:
let fps = 30;

// Params of MOT task (to display debug mode):
let max_angle = 18;
let min_angle = 6;


// Variables needed for object in canvas:
let canvas, hover_color, app;
let answer_phase = false;
let parameter_dict = {};
let results = {};
let numbers = [];
let exit;
let mode;
let arena_background,arena_background_init, button_play, button_tuto, button_exit, button_pause, button_keep,
    button_answer, button_next_episode;
let background_size;
let button_exit_width = 100;
let button_exit_height = 45;
let button_height = 60;
let button_width = 120;

let guard_image, goblin_image, leaf_image,
    sec_task, gill_font_light, gill_font, timer_image;
let screen_params = false;
let pres_timer, tracking_timer, answer_timer, probe_timer, time_step, game_time;
let paused = false;

// inputs for params pannel:
let screen_params_input, angle_max_input, angle_min_input,debug_input, activity_type_input,
    n_targets_input, n_distractors_input, speed_max_input, speed_min_input, radius_input,
    presentation_time_input, fixation_time_input, tracking_time_input, SRI_max_input, RSI_input,
    delta_orientation_input, step, labels_inputs, inputs_map, key_val, button_params, n_targets_slider,
    dict_pannel, angle_max_slider, angle_min_slider, n_distractors_slider, speed_max_slider,
    speed_min_slider, radius_slider, secondary_task_input, gaming_input, gaming_description,
    presentation_time_slider, fixation_time_slider, tracking_time_slider, SRI_max_slider, RSI_slider,
    delta_orientation_slider, screen_params_description, angle_max_description
    ,angle_min_description, debug_description, secondary_task_description, n_targets_description,
    n_distractors_description,speed_max_description,speed_min_description,radius_description,
    presentation_time_description, fixation_time_description, tracking_time_description, SRI_max_description,
    RSI_description, delta_orientation_description, button_hide_params, hidden_pannel, button_raz_params,game_timer;


let default_params = {
        n_targets: 1, n_distractors: 2, angle_max: 9, angle_min: 3,
        radius: 1, speed_min: 4, speed_max: 4, nb_target_retrieved: 0, nb_distract_retrieved: 0,
        presentation_time: 1, fixation_time: 1, tracking_time: 7,
        debug: 0, secondary_task: 'none', SRI_max: 2, RSI: 1,
        delta_orientation: 45, gaming: 1, probe_time: 3 };


// clear session storage:
sessionStorage.clear();

