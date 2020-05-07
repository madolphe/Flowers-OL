// Log function
function logGame(metrics) {
    let s = new String;
    for (let [key, value] of Object.entries(metrics)) {
        s = s.concat(`${key}: ${value}<br>`)
    };
    document.getElementById("game-log").innerHTML = s;
};

// Set the name of the hidden property and the change event for visibility
let hidden, visibilityChange; 
if (typeof document.hidden !== "undefined") { // Opera 12.10 and Firefox 18 and later support 
  hidden = "hidden";
  visibilityChange = "visibilitychange";
} else if (typeof document.msHidden !== "undefined") {
  hidden = "msHidden";
  visibilityChange = "msvisibilitychange";
} else if (typeof document.webkitHidden !== "undefined") {
  hidden = "webkitHidden";
  visibilityChange = "webkitvisibilitychange";
};

// Warn if the browser doesn't support addEventListener or the Page Visibility API
if (typeof document.addEventListener === "undefined" || hidden === undefined) {
  alert("This demo requires a browser, such as Google Chrome or Firefox, that supports the Page Visibility API.");
};