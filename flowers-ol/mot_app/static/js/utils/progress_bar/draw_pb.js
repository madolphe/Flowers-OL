let sucess, bar;
let fname_sucess = 'static/images/icons/success.png';

function preload(){
    success = loadImage(fname_sucess);
}
function setup(){
    let cnv = createCanvas(400, 90);
    cnv.parent("progress_bar");
    bar = new progressBar(5);
}
function draw(){
    bar.draw();
}