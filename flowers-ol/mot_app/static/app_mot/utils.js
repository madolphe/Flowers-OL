function set_screen_params(){
    diagcm = parameter_dict['screen_params'];
    max_angle = parameter_dict['angle_max']*2;
    min_angle = parameter_dict['angle_min']*2;
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
    ppd = cmpd * pixpcm;
}
function post(path, params, method='post') {
    // Function to ask for parameters of new episode
    // first create an hidden form:
    let form = document.getElementById('request');
    form.method = method;
    form.action = path;
    // Pass all parameters needed:
    for (const key in params) {
        if (params.hasOwnProperty(key)) {
          const hiddenField = document.createElement('input');
          hiddenField.type = 'hidden';
          hiddenField.name = key;
          hiddenField.value = params[key];
          form.appendChild(hiddenField)}
    }
    document.body.appendChild(form);
    form.submit();
}
p5.Vector.prototype.reflect = function reflect(surfaceNormal) {
    // First normalize normal:
    surfaceNormal.normalize();
   return this.sub(surfaceNormal.mult(2 * this.dot(surfaceNormal)));
};


