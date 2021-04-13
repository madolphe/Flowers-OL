// number of pixels per degres:
let viewer_dist = 50;
// let screen_params = 1920/34.25; // width pixels/cm in sawayama's monitor
let ppcm = screen.availWidth / screen_params
let ppd = get_ppd(viewer_dist, ppcm);

function get_ppd(viewer_dist, screen_params){
    return (viewer_dist*Math.tan(Math.PI/180)) * screen_params;
}

iframe = document.getElementById("iframe_tutorial");
iframe.width = Math.round(12*ppd);
iframe.height = Math.round(10*ppd);

