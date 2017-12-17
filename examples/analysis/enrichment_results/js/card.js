/**
 * Created by sheep on 2017/8/11.
 */

// $.getJSON("data/card.json",function(config){
//     console.log("main");
//     for (var i in config) {
//         console.log(i);
//         if (config[i].type == 'chart') {
//             init_chart(i, config[i].snap);
//         } else if (config[i].type == 'graph') {
//             init_graph(i, config[i].snap);
//         }
//     }
// });

var config = {"plot1": {"type": "chart", "snap": {"grid": {"bottom": "3%", "right": "12%", "left": "3%", "top": "5%", "containLabel": true}, "color": ["#F2F2F2"], "xAxis": {"type": "value", "splitLine": {"show": false}, "lineColor": "transparent", "name": "-lg(p_bonferroni)", "boundaryGap": [0, 0.01]}, "yAxis": {"type": "category", "splitLine": {"show": false}, "data": ["catalytic activity            ", "transferase activity          ", "catalytic activity, acting on a protein", "cellular protein modification process", "protein modification process  ", "protein phosphorylation       ", "palmitoyl-(protein) hydrolase activity", "palmitoyl hydrolase activity  "]}, "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}}, "series": [{"type": "bar", "data": [12.556529137977249, 11.52642710618783, 11.404091563263778, 4.304718804855139, 4.304718804855139, 3.9192059180417576, 3.0709665213541433, 3.0709665213541433], "name": "-lg(p_bonferroni)"}]}, "detail": {"method": "ORA"}}, "plot0": {"type": "chart", "snap": {"grid": {"bottom": "3%", "right": "12%", "left": "3%", "top": "5%", "containLabel": true}, "color": ["#F2F2F2"], "xAxis": {"type": "value", "splitLine": {"show": false}, "lineColor": "transparent", "name": "-lg(p_bonferroni)", "boundaryGap": [0, 0.01]}, "yAxis": {"type": "category", "splitLine": {"show": false}, "data": ["catalytic activity            ", "transferase activity          ", "catalytic activity, acting on a protein", "cellular protein modification process", "protein modification process  ", "protein phosphorylation       ", "palmitoyl-(protein) hydrolase activity", "palmitoyl hydrolase activity  "]}, "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}}, "series": [{"type": "bar", "data": [12.556529137977249, 11.52642710618783, 11.404091563263778, 4.304718804855139, 4.304718804855139, 3.9192059180417576, 3.0709665213541433, 3.0709665213541433], "name": "-lg(p_bonferroni)"}]}, "detail": {"method": "ORA"}}};

window.onload = function (args) {
    console.log("main");
    for (var i in config) {
        console.log(i);
        if (config[i].type == 'chart') {
            init_chart(i, config[i].snap);
        } else if (config[i].type == 'graph') {
            init_graph(i, config[i].snap);
        }
    }
};


function init_chart(id, config) {
    var chart = echarts.init(document.getElementById(id));
    chart.setOption(config);
}


function init_graph(id, config) {
    node_dict = {};
    for (var i in config.options.elements) {
        var e = config.options.elements[i];
        if (e.group == "nodes") {
            node_dict[e.data.id] = e;
        }
    }
    config.options['container'] = document.getElementById(id);
    cy = cytoscape(config.options);
    var callback = function (ele, event, type) {
        console.log("target: ", ele);
        var target = '';
        for (var i in config.elements){
            if (config.elements[i].data.id == ele.id()){
                target = config.elements[i];
            }
        }
        if (type == 'Expand') {
            // first read the expand selection
            console.log(event.cyTarget.id());
            var setting = node_dict[event.cyTarget.id()].expand;
            if (setting == undefined) {
                return;
            }
            if (setting.source == 'local'){
                // read the id from targets
                var needsToAdd = [];
                for (var i in setting.targets) {
                    var id = setting.targets[i];
                    var new_node = jQuery.extend(true, {}, default_node);
                    // new_node.data.id =
                    var node = new_dict[id];
                    new_node.data = node;
                    new_node.data['label'] = new_node.data.name;
                    new_node.position.x = 1000;
                    new_node.position.y = 1000;
                    var new_edge = jQuery.extend(true, {}, default_edge);
                    new_edge.data.id = 'edge' + event.cyTarget.id() + node.id;
                    new_edge.data.source = event.cyTarget.id();
                    new_edge.data.target = node.id;
                    console.log(new_edge);
                    console.log(new_node);
                    cy.add(new_node);
                    cy.add(new_edge);
                }
                cy.layout({
                    'name': 'dagre'
                })
            }
            // console.log(setting);
        }else if (type == 'Remove') {
            cy.remove(ele);
        }else if (type == 'Mark'){
            // var tgt = cy.$("#" + ele.id());
            // console.log(tgt);
            ele.css('background-color', 'red')
        }
    };
    var defaults = {
        menuRadius: 100, // the radius of the circular menu in pixels
        selector: 'node', // elements matching this Cytoscape.js selector will trigger cxtmenus
        commands: [ // an array of commands to list in the menu or a function that returns the array
            {
                fillColor: 'rgba(20, 20, 20, 0.75)',
                content: "Mark", // html/text content to be displayed in the menu
                select: function (ele, event) {
                    callback(ele, event, 'Mark')
                }
            },
            {
                fillColor: 'rgba(20, 20, 20, 0.75)',
                content: "Expand", // html/text content to be displayed in the menu
                select: function (ele, event) {
                    callback(ele, event, 'Expand')
                }
            },
            {
                fillColor: 'rgba(20, 20, 20, 0.75)',
                content: "Remove", // html/text content to be displayed in the menu
                select: function (ele, event) {
                    callback(ele, event, 'Remove')
                }
            }
        ], // function( ele ){ return [ /*...*/ ] }, // example function for commands
        fillColor: 'rgba(0, 0, 0, 0.75)', // the background colour of the menu
        activeFillColor: 'rgba(92, 194, 237, 0.75)', // the colour used to indicate the selected command
        activePadding: 20, // additional size in pixels for the active command
        indicatorSize: 24, // the size in pixels of the pointer to the active command
        separatorWidth: 3, // the empty spacing in pixels between successive commands
        spotlightPadding: 4, // extra spacing in pixels between the element and the spotlight
        minSpotlightRadius: 24, // the minimum radius in pixels of the spotlight
        maxSpotlightRadius: 38, // the maximum radius in pixels of the spotlight
        openMenuEvents: 'cxttapstart taphold', // space-separated cytoscape events that will open the menu; only `cxttapstart` and/or `taphold` work here
        itemColor: 'white', // the colour of text in the command's content
        itemTextShadowColor: 'black', // the text shadow colour of the command's content
        zIndex: 9999, // the z-index of the ui div
        atMouse: false // draw menu at mouse position
    };
    var cxtmenuApi = cy.cxtmenu( defaults );
    cy.on('tap', 'node', function(evt){
        console.log( evt.cyTarget.id() );
    });
    cy.on('mouseover', 'node', function (evt) {
        $(".qtip-content").remove();
        $(".qtip").remove();
        // console.log("over");
        // console.log(evt.cyTarget.id());
        var tip = node_dict[evt.cyTarget.id()].tooltip;
        if (tip == undefined) {
            return;
        }
        var text = "";
        for (var i in tip){
            // if (i == 'Name'){
            //     continue;
            // }
            text += i + ": " + tip[i] + "</br>";
        }
        evt.cyTarget.qtip({
            style: {
                classes: 'qtip-tipsy'
            },
            content: {
                text: text
            },
            show: {
                ready: true
            }
        })
    });
    cy.on('mouseout', 'node', function (evt) {
        $(".qtip-content").remove();
        $(".qtip").remove();
    });
}