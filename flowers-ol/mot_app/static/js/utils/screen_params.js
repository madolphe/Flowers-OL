/**
 * [get_ppd description]
 * @param  {double} viewer_dist [description]
 * @param  {double} diagcm [description]
 * @return {double}     [description]
 */
function get_ppd(viewer_dist, diagcm){
    // screen size in pixels:
    screen_width_px = screen.availWidth;
    screen_height_px = screen.availHeight;
    // size of diag in pixels:
    diagpx = Math.sqrt(screen_width_px**2 + screen_height_px**2);
    // size of screen in cm:
    screen_width = screen_width_px * diagcm / diagpx;
    screen_height = screen_height_px * diagcm / diagpx;
    // nbr of pixels per cm:
    pixpcm = screen_width_px/screen_width;
    // Just to check: pix_x should be approx the same :
    // console.log(pixpcm, $(window).height()/screen_height);
    // cm per deg:
    cmpd = viewer_dist*Math.tan(Math.PI/180);
    // pixels per deg:
    let res = cmpd * pixpcm
    return(res)
}