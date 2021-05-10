let sucess, bar;
let fname_sucess = 'static/images/icons/success.png';

function preload(){
    success = loadImage(fname_sucess);
}
function setup(){
    let cnv = createCanvas(400, 90);
    cnv.parent("progress_bar");
    bar = new progressBar(index_task);
}
function draw(){
    frameRate(1);
    bar.draw();
}