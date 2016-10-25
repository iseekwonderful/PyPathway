/**
 * Created by sheep on 16/8/10.
 */
// this file tell the application of the handling of events.

var configFile = "kegg_data/config.json";
var configData = undefined;
var qtip_state = undefined;
var highlights = undefined;
var element_styles = [];
var additionalEdges = [];
var additionalScale = [];
var qtipReady = true;

function clean_qtip() {
    var selected = $(".qtip");
    selected.remove();
    if (qtip_state != undefined){
        console.log("exist" + qtip_state.qtip);
    }
    $("#qtip-content").remove();
    // if (qtip_state != undefined){
    //     qtip_state.qtip('destroy');
    // }
    var tips = $(".qtip-pos-tc");
    tips.remove();
}

// function init_hook() {
//     // hook the init procedure
//     // do some thing here
//     // var path_to_xml = "neuronal_muscle_signalling.xml";
//     var path_to_xml = "../sampleapp-components/data/pathway.xml";
//     loadSample(path_to_xml);
//     console.log("Hooked");
// }

function resertProps() {
    // clean_qtip()
    for (var x in additionalScale){
        console.log(additionalScale);
        additionalScale[x][0].css("width", additionalScale[x][1]);
        additionalScale[x][0].css("height", additionalScale[x][2]);
    }
    additionalScale = [];
    for (var x in element_styles){
        console.log(element_styles);
        element_styles[x][0].css(element_styles[x][1], element_styles[x][2]);
    }
    // if (highlights != undefined){
    //     for (var x in element_styles){
    //         highlights.css(element_styles[x][0], element_styles[x][1]);
    //     }
    // }
    element_styles = [];
    if (additionalEdges.length > 0){
        for(var x in additionalEdges){
            cy.remove(cy.$("#" + additionalEdges[x]));
        }
    }
    additionalEdges = [];
}

function value_change_hook(){
    $.getJSON(configFile, function (data) {
        configData = data["option"];
        console.log(configData);
        // when init here we want to set the default value
        for(var k in configData){
            var elememt = cy.$("#" + k);
            // console.log(k, elememt);
            var defaults = configData[k].default;
            for(var x in defaults){
                if (x == "value_changed") {
                    for (var k in defaults[x]) {
                        elememt.css(k, defaults[x][k]);
                    }
                }
            }
        }
    });
}

function applyValueChange(element, config){
    for(var x in config){
        if (x == "scale"){
            element_styles.push([element, "width", element.css("width")]);
            element_styles.push([element, "height", element.css("height")]);
            element.css("width", parseFloat(element.css("width")) *
                                parseFloat(config[x]));
            element.css("height", parseFloat(element.css("height")) *
                                parseFloat(config[x]));
        }else {
            element_styles.push([element, x, element.css(x)]);
            element.css(x, config[x])
        }
    }
    // highlights = element;
    // console.log(element_styles);
}

function applyLink(element, config) {
    if (!qtipReady){
        return
    }
    qtipReady = false;
    setTimeout(function(){
        qtipReady = true;
    },100);
    clean_qtip();
    element.qtip({
        content: {
            text: "<div style='padding: 4px'><a href='"
            + config["url"] + "' target='_blank'>"
            + config.name
            + "</div>"
        },
        style: {
            classes: 'qtip-bootstrap',
            tip: {
                width: 16,
                height: 8
            }
        },
        show: {
            ready: true
        },
        adjust: {
            screen: true
        },
        hide: {
            event: 'unfocus',
            fixed: true,
            delay: 0
        },
        position: {
            viewport: $(window)
        }
    });
}

function applyNodeConnection(element, config) {

}

// generate qtip for certain node
function generate_tip(element, config){
    if (!qtipReady){
        return
    }
    qtipReady = false;
    setTimeout(function(){
        qtipReady = true;
    },100);
    clean_qtip();
    var content = make_tip_node(config);
    qtip_state = element;
    element.qtip({
        content: {
            text: $("#qtip-content")
            // text: content
        },
        style: {
            classes: 'qtip-bootstrap',
            tip: {
                width: 16,
                height: 8
            }
        },
        show: {
            ready: true
        },
        adjust: {
            screen: true
        },
        hide: {
            event: 'unfocus',
            fixed: true,
            delay: 100
        },
        position: {
            my: "top center",
            at: "bottom center",
            viewport: $(window)
        }
    });
}

// generate custom qtip content for node
function make_tip_node(config){
    // var qtips = $("#qtip-content");
    // qtips.remove();
    var w = config.width;
    var h = config.height;
    config = config.tab;
    console.log(w, h);
    var content = $("<div></div>");
    content.attr("id", "qtip-content");
    content.css({"width": w + 'px', 'height': h + 'px', 'padding': '2px'});
    content.hide();
    var echartargs = [];
    var tab = $("<ul id='mytab' style='width: " + (w - 6) + "px;' class='nav nav-tabs nav-justified'></ul>");
    var view = $("<div id='tabview' style='width: " + (w - 6) + "px; height: " + (h - 24) + "px;' class='tab-content'></div>");
    // this config, is a tab-list, may contain the tab we list in the docs.
    // here should be meet only a list.
    if (config.length == 0){
        return null;
    }else {
        // multiple tab
        var count = 0;
        for (var x in config) {
            var c = config[x];
            console.log(c);
            var sub = $("<li></li>");
            if (count == 0){
                sub.attr("class", "active")
            }
            var a = $("<a href='#" + c[1].name + "' data-toggle='tab'>" + c[1].name + "</a>");
            a.appendTo(sub);
            sub.appendTo(tab);
            // add view
            var sub2 = $("<div style='padding-top: 5px; padding-left: 5px;width: " + (w - 12) + "px; height: " + (h - 50) +"px;' id='" + c[1].name + "'></div>");
            if (count == 0){
                sub2.attr("class", "tab-pane fade in active");
            }else{
                sub2.attr("class", "tab-pane fade");
            }
            if (c[0] == "image"){
                $("<img class='img-responsive' src='" + c[1].url + "'/>").appendTo(sub2);
            }else if (c[0] == "chart"){
                var f = function (name, option) {
                    var chart = echarts.init(document.getElementById(name));
                    chart.setOption(option);
                };
                var op = c[1].option;
                var id = c[1].name;
                echartargs.push([f, [id, op]]);
                // this is a echart drawing:
            }else if (c[0] == "table"){
                var tb = $("<table class='table table-striped'></table>");
                for (var r in c[1].table){
                    var tr = $("<tr></tr>");
                    for (var cl in c[1].table[r]){
                        $("<td>" + c[1].table[r][cl] + "</td>").appendTo(tr);
                        console.log(c[1].table[r][cl]);
                    }
                    tr.appendTo(tb)
                }
                tb.appendTo(sub2);
            }else if (c[0] == "model"){
                // $("<div id='model-area'></div>").appendTo(sub2);
                // var element = $('#model-area');
                // var model_config = { defaultcolors: $3Dmol.rasmolElementColors, backgroundColor: 'white' };
                // var viewer = $3Dmol.createViewer( element, model_config );
                // console.log("loading");
                // var pdbUri = 'https://files.rcsb.org/download/5HWC.pdb';
                // jQuery.ajax( pdbUri, {
                // success: function(data) {
                //     var v = viewer;
                //     v.addModel( data, "pdb" );                       /* load data */
                //     v.setStyle({}, {cartoon: {color: 'spectrum'}});  /* style all atoms */
                //     v.zoomTo();                                      /* set camera */
                //     v.render();                                      /* render scene */
                //     v.zoom(1.2, 1000);                               /* slight zoom */
                // },
                // error: function(hdr, status, err) {
                //     console.error( "Failed to load PDB " + pdbUri + ": " + err );
                // }
                // })
            }
            sub2.appendTo(view);
            count ++;
        }
        tab.appendTo(content);
        view.appendTo(content);
        content.appendTo('body');
        console.log("append");
        for (var x in echartargs){
            echartargs[x][0](echartargs[x][1][0], echartargs[x][1][1]);
        }
        return content;
    }
}

function apply_action(action, target){
    // action: event type
    // target: the target element id
    if (target.id() in configData){
        if (Object.keys(configData[target.id()][action]).length > 0){
            var config = configData[target.id()][action];
            if ("value_changed" in config){
                applyValueChange(target, config["value_changed"]);
            }
            // note that if one node has its popup, will overwrite the link
            if ("popup" in config){
                generate_tip(target, config["popup"])
            }else if ("link" in config){
                applyLink(target, config["link"]);
            }
            // the connect reconstruction
            if ("connection" in config){
                console.log(config["connection"]);
                for (var x in config["connection"]){
                    cy.add({
                        group: "edges",
                        data: { id: target.id() + config["connection"][x][0],
                        source: config["connection"][x][0], target: target.id()}
                    });
                    var newElement = cy.$("#" + target.id() + config["connection"][x][0]);
                    for (var t in config["connection"][x][1]){
                        if (t == "target-style" && !(config["connection"][x][1][t] == undefined)){
                            console.log(config["connection"][x][1][t]);
                            applyValueChange(cy.$("#" + config["connection"][x][0]),
                                config["connection"][x][1][t].value_changed
                            );
                        }else {
                            newElement.css(t, config["connection"][x][1][t]);
                        }
                    }
                    additionalEdges.push(target.id() + config["connection"][x][0]);
                }
            }
        }
    }else{
        console.log("over", "no action");
    }

}

function go_default(){

}

function on_mouse_over(event) {
    var target = event.cyTarget;
    // let us check if its background or edge!
    if (event.cyTarget == cy || !event.cyTarget.isNode()){
        return;
    }
    apply_action("over", target);
    // if (target.id() in configData){
    //     if (Object.keys(configData[target.id()]["over"]).length > 0){
    //         var config = configData[target.id()]["over"];
    //         console.log(config);
    //         if ("value_changed" in config){
    //             // applyValueChange(target, config["value_changed"]);
    //         }
    //         if ("popup" in config){
    //             generate_tip(target, config["popup"])
    //         }else if ("link" in config){
    //             applyLink(target, config["link"]);
    //         }
    //     }
    // }else{
    //     console.log("over", "no action");
    // }
}

function on_mouse_out(event) {
    // let us check if its background or edge!
    if (event.cyTarget == cy || !event.cyTarget.isNode()){
        return;
    }
    console.log("out", event);
    resertProps();
    // console.log("out");
    // trying to resume to the default state
}

function on_mouse_down(event){
    // let us check if its background or edge!
    if (event.cyTarget == cy || !event.cyTarget.isNode()){
        return;
    }
    resertProps();
    console.log("down", event.cyTarget.id());
    apply_action("left", event.cyTarget);
    //generate_tip(event.cyTarget, configData[event.cyTarget.id()].left[0]);
    // cy.nodes($("#glyph4")).style({'background-color': 'yellow'});
}

function on_mouse_up(event) {
    // let us check if its background or edge!
    // if (event.cyTarget == cy || !event.cyTarget.isNode()){
    //     return;
    // }
    // console.log("up", event);
    // console.log("up");
}
function right_click(event) {
    if (event.cyTarget == cy || !event.cyTarget.isNode()){
        return;
    }
    resertProps();
    console.log("right", event.cyTarget.id());
    apply_action("right", event.cyTarget);
}

function customeQtip(node) {
    var label = node._private.data.sbgnlabel;

    if (label == null || label == "")
        label = getInfoLabel(node);

    if (label == null || label == "")
        return;

    node.qtip({
        content: function () {
            var contentHtml = "<b style='text-align:center;font-size:16px;'>" + label + "</b>";
            var sbgnstatesandinfos = node._private.data.sbgnstatesandinfos;
            for (var i = 0; i < sbgnstatesandinfos.length; i++) {
                var sbgnstateandinfo = sbgnstatesandinfos[i];
                if (sbgnstateandinfo.clazz == "state variable") {
                    var value = sbgnstateandinfo.state.value;
                    var variable = sbgnstateandinfo.state.variable;
                    var stateLabel = (variable == null /*|| typeof stateVariable === undefined */) ? value :
                    value + "@" + variable;
                    if (stateLabel == null) {
                        stateLabel = "";
                    }
                    contentHtml += "<div style='text-align:center;font-size:14px;'>" + stateLabel + "</div>";
                }
                else if (sbgnstateandinfo.clazz == "unit of information") {
                    var stateLabel = sbgnstateandinfo.label.text;
                    if (stateLabel == null) {
                        stateLabel = "";
                    }
                    contentHtml += "<div style='text-align:center;font-size:14px;'>" + stateLabel + "</div>";
                }
            }
            return contentHtml;
        },
        show: {
            ready: true
        },
        position: {
            my: 'top center',
            at: 'bottom center',
            adjust: {
                cyViewport: true
            }
        },
        style: {
            classes: 'qtip-bootstrap',
            tip: {
                width: 16,
                height: 8
            }
        }
    });
}