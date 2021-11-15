console.log(participants_staircase_data)
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

let layout = {
    legend:{font:{color:"white"}},
    autosize: true,
    title: {
        text: 'Evolution of mean nb_targets through training',
        font:{color:'white'}
    },
    paper_bgcolor: "black",
    plot_bgcolor: "black",
    xaxis: {
        automargin: true,
        title:{
            text: 'Session date',
            font:{color: 'white'},
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
        title:{
            text: 'nb_targets',
            font:{color: 'white'}
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
        {y: 0.8, yanchor: 'top', pad: {'r':20 },buttons: buttons_participant}
    ]
}

function makeTrace(participant) {
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

// for now just print the average lvl for each session
Plotly.newPlot(
    'plotly_div_stairase',
    participants_staircase_array.map(makeTrace),
    layout
);

