let my_req;
let index_frame = 0;
update_timestep_display();

// Prepare some variables
// create buttons_array for each participant in the baseline
// each button should be a dict like: {method:'restyle', args:[...], label: participant_name}
let buttons_participant = []
let arg_visible = []
let all_visible = []
for (var i = 0; i < participants_staircase_array.length; i++) {
    arg_visible.push(false);
    all_visible.push(true);
}
all_participants = {
    method: 'restyle',
    args: ['visible', all_visible],
    label: 'all',
}
buttons_participant.push(all_participants)
var count = 0;
participants_staircase_array.forEach(element => {
        var clone = JSON.parse(JSON.stringify(arg_visible));
        clone[count] = true;
        buttons_participant.push({
            method: 'restyle',
            args: ['visible', clone],
            label: element
        });
        count++;
    }
)

// Layout used to display the data
let layout_nb = {
    legend: {font: {color: "white"}},
    autosize: true,
    showlegend: false,
    title: {
        text: 'Evolution of mean nb_targets through training',
        font: {color: 'white'}
    },
    paper_bgcolor: "black",
    plot_bgcolor: "black",
    xaxis: {
        automargin: true,
        title: {
            text: 'Session date',
            font: {color: 'white'},
            standoff: 20
        },
        tickmode: 'linear',
        zerolinecolor: 'white',
        linecolor: 'white',
        tickfont: {
            color: 'white',
        }
    },
    yaxis: {
        title: {
            text: 'nb_targets',
            font: {color: 'white'}
        },
        linecolor: 'white',
        zerolinecolor: 'white',
        gridcolor: 'grey',
        tickfont: {
            color: 'white'
        }
    },
    margin: {
        b: 50,
    },
    updatemenus: [
        {y: 0.5, yanchor: 'top', pad: {'r': 40}, buttons: buttons_participant}
    ]
}
let layout_idle = {
    legend: {font: {color: "white"}},
    autosize: true,
    title: {
        text: 'Evolution of mean idle through training',
        font: {color: 'white'}
    },
    paper_bgcolor: "black",
    plot_bgcolor: "black",
    xaxis: {
        automargin: true,
        title: {
            text: 'Session date',
            font: {color: 'white'},
            standoff: 20
        },
        tickmode: 'linear',
        zerolinecolor: 'white',
        linecolor: 'white',
        tickfont: {
            color: 'white',
        }
    },
    yaxis: {
        title: {
            text: 'mean_idle',
            font: {color: 'white'}
        },
        linecolor: 'white',
        zerolinecolor: 'white',
        gridcolor: 'grey',
        tickfont: {
            color: 'white'
        }
    },
    margin: {
        b: 50,
    },
    updatemenus: [
        {y: 0.5, yanchor: 'top', pad: {'r': 40}, buttons: buttons_participant}
    ]
}
let layout_traj = {
    legend: {font: {color: "white"}},
    autosize: true,
    title: {
        text: 'Trajectories of participants through training',
        font: {color: 'white'}
    },
    paper_bgcolor: "black",
    plot_bgcolor: "black",
    margin: {
        b: 50,
    },
    polar: {
        angularaxis: {
            visible: true,
            color: "white",
            gridcolor: "black",
            range: [0, 7],
            title: {
                font: {
                    color: "white"
                }
            }
        },
        radialaxis: {
            visible: true,
            range: [0, 7],
            title: {
                font: {
                    color: "white"
                }
            }
        },

    }
}
let layout_para_hull = {
    legend: {font: {color: "white"}},
    autosize: true,
    title: {
        text: 'Parallel plot of convex hulls points',
        font: {color: 'white'}
    },
    color: {
        line: {
            color: 'white'
        }
    },

    paper_bgcolor: "black",
    plot_bgcolor: "black",
    margin: {
        b: 50,
    }
}


// Data to be displayed for each plot (and for all participants)
function makeTrace_nb(participant) {
    let y_mean = [];
    let y_std = [];
    let x = [];
    for (var key in participants_staircase_data[participant][0]) {
        y_mean.push(participants_staircase_data[participant][0][key]);
        y_std.push(participants_staircase_data[participant][1][key]);
        x.push(key);
    }
    return {
        y: y_mean,
        x: x,
        error_y: {
            type: 'data',
            array: y_std,
            visible: true,
        },
        line: {
            shape: 'scatter',
        },
        name: participant,
    };
}

function makeTrace_idle(participant) {
    let y_mean = [];
    let x = [];
    for (var key in participants_staircase_data[participant][0]) {
        y_mean.push(participants_staircase_data[participant][2][key]);
        x.push(key);
    }
    return {
        y: y_mean,
        x: x,
        line: {
            shape: 'scatter',
        },
        name: participant,
    };
}

function makeTrace_traj(participant) {
    let r = [];
    if (participants_staircase_data[participant][3]['n_targets'].length > index_frame) {
        r.push(participants_staircase_data[participant][3]['n_targets'][index_frame])
        r.push(participants_staircase_data[participant][3]['speed'][index_frame])
        r.push(participants_staircase_data[participant][3]['tracking_duration'][index_frame])
        r.push(participants_staircase_data[participant][3]['probe_duration'][index_frame])
        r.push(participants_staircase_data[participant][3]['radius'][index_frame])
        r.push(participants_staircase_data[participant][3]['n_targets'][index_frame])
    }
    return {
        r: r,
        type: 'scatterpolar',
        theta: ['n_targets', 'speed', 'tracking_duration', 'probe_duration', 'radius', 'n_targets'],
        name: participant,
    };
}

function makeTrace_para_hull(participant, dict) {
    let [session_id, values_ntargets, values_speed, values_probe_time, values_tracking_time, values_radius] = [[], [], [], [], [], []];
    let session_index = 0
    for (var session in dict[participant][0]) {
        for (var i = 0; i < dict[participant][0][session].length; i++) {
            session_id.push(session_index)
            values_ntargets.push(dict[participant][0][session][i][0])
            values_speed.push(dict[participant][0][session][i][1])
            values_probe_time.push(dict[participant][0][session][i][2])
            values_tracking_time.push(dict[participant][0][session][i][3])
            values_radius.push(dict[participant][0][session][i][4])
        }
        session_index ++;
    }
    return [{
        type: 'parcoords',
        line: {
            color: session_id
        },
        dimensions: [
        {
            range: [0, 10],
            label: 'session_index',
            values: session_id,
            constraintrange: [0,1]
        },
            {
            range: [0, 8],
            label: 'n_targets',
            values: values_ntargets,
        }, {
            range: [1, 6],
            label: 'speed',
            values: values_speed,
        }, {
            range: [2, 7],
            label: 'probe_time',
            values: values_probe_time
        },
        {
            range: [5.5, 13],
            label: 'tracking_time',
            values: values_tracking_time,
        },
        {
            range: [0.5, 1.5],
            label: 'radius',
            values: values_radius,
        }
        ]
    }]
}

function makeTrace_mean_para_hull(participant, dict) {
    let [session_id, values_ntargets, values_speed, values_probe_time, values_tracking_time, values_radius] = [[], [], [], [], [], []];
    let session_index = 0
    const average = arr => arr.reduce( ( p, c ) => p + c, 0 ) / arr.length;
    for (var session in dict[participant][0]) {
        let [tmp_values_ntargets, tmp_values_speed, tmp_values_probe_time, tmp_values_tracking_time, tmp_values_radius] = [[], [], [], [], []];
        for (var i = 0; i < dict[participant][0][session].length; i++) {
            tmp_values_ntargets.push(dict[participant][0][session][i][0])
            tmp_values_speed.push(dict[participant][0][session][i][1])
            tmp_values_probe_time.push(dict[participant][0][session][i][2])
            tmp_values_tracking_time.push(dict[participant][0][session][i][3])
            tmp_values_radius.push(dict[participant][0][session][i][4])
        }
        session_id.push(session_index)
        values_ntargets.push(average(tmp_values_ntargets))
        values_speed.push(average(tmp_values_speed))
        values_probe_time.push(average(tmp_values_probe_time))
        values_tracking_time.push(average(tmp_values_tracking_time))
        values_radius.push(average(tmp_values_radius))
        session_index ++;
    }
    return [{
        type: 'parcoords',
        line: {
            color: session_id
        },
        dimensions: [
        {
            range: [0, 10],
            label: 'session_index',
            values: session_id,
            constraintrange: [0,1]
        },
            {
            range: [0, 8],
            label: 'n_targets',
            values: values_ntargets,
        }, {
            range: [1, 6],
            label: 'speed',
            values: values_speed,
        }, {
            range: [2, 7],
            label: 'probe_time',
            values: values_probe_time
        },
        {
            range: [5.5, 13],
            label: 'tracking_time',
            values: values_tracking_time,
        },
        {
            range: [0.5, 1.5],
            label: 'radius',
            values: values_radius,
        }
        ]
    }]
}

// Draw all the plots:
Plotly.newPlot(
    'plotly_div_stairase_nb',
    participants_staircase_array.map(makeTrace_nb),
    layout_nb
);
Plotly.newPlot(
    'plotly_div_stairase_idle',
    participants_staircase_array.map(makeTrace_idle),
    layout_idle
)
Plotly.newPlot(
    'plotly_div_animate',
    participants_staircase_array.map(makeTrace_traj),
    layout_traj
)
var trace = {
  type: 'parcoords',
  line: {
    color: 'blue'
  },
  dimensions: [{
    range: [1, 5],
    constraintrange: [1, 2],
    label: 'A',
    values: [1,4]
  }, {
    range: [1,5],
    label: 'B',
    values: [3,1.5],
    tickvals: [1.5,3,4.5]
  }, {
    range: [1, 5],
    label: 'C',
    values: [2,4],
    tickvals: [1,2,4,5],
    ticktext: ['text 1','text 2','text 4','text 5']
  }, {
    range: [1, 5],
    label: 'D',
    values: [4,2]
  }]
};

var data = [trace]

// Plotly.newPlot(
//     'plotly_div_hull_para',
//     //participants_zpdes_array.map(makeTrace_para_hull),
//     makeTrace_para_hull('Axelle', cumu_true_hull_points_per_participant)
//     // data
// )
Plotly.newPlot(
    'plotly_div_hull_para',
    //participants_zpdes_array.map(makeTrace_para_hull),
    makeTrace_mean_para_hull('Axelle', ps_true_hull_points_per_participant)
    // data
)



// Animations functions:
function update_timestep_display() {
    document.getElementById('time_step').innerHTML = index_frame
}

function launch_animation() {
    update();
}

function update() {
    index_frame++;
    update_timestep_display();
    Plotly.animate(
        'plotly_div_animate',
        {data: participants_staircase_array.map(makeTrace_traj)},
        {
            transition: {
                duration: 1
            },
            frame: {
                duration: 5,
                redraw: true
            }
        },
        layout_traj
    )
    if (index_frame < 10000) {
        my_req = requestAnimationFrame(update);
    } else {
        index_frame = 0;
    }
}

function stop_animation() {
    index_frame = 0;
    update_timestep_display();
    cancelAnimationFrame(my_req);
    Plotly.animate(
        'plotly_div_animate',
        {data: participants_staircase_array.map(makeTrace_traj)},
        {
            transition: {
                duration: 1
            },
            frame: {
                duration: 5,
                redraw: true
            }
        },
        layout_traj
    )
}

