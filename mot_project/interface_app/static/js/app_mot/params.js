// Screen params:
let diagcm = 39.116;
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


// Params of MOT task:
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
let arena_background, button_play, button_tuto, button_exit, button_pause,
    button_answer, button_next_episode, guard_image, goblin_image;
let screen_params = false;

// clear session storage:
sessionStorage.clear();

