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

var config = {"plot1": {"type": "chart", "snap": {"xAxis": {"boundaryGap": [0, 0.01], "type": "value", "name": "-lg(p_bonferroni)", "lineColor": "transparent", "splitLine": {"show": false}}, "color": ["#F2F2F2"], "grid": {"bottom": "3%", "left": "3%", "containLabel": true, "right": "12%", "top": "5%"}, "series": [{"type": "bar", "data": [13.321281912243151, 11.556529137977249, 4.307572801910292, 4.307572801910292, 3.9213901653036336, 3.083141235300246, 3.083141235300246, 2.237863830098888], "name": "-lg(p_bonferroni)"}], "tooltip": {"axisPointer": {"type": "shadow"}, "trigger": "axis"}, "yAxis": {"type": "category", "data": ["catalytic activity", "transferase activity", "protein modification process", "cellular protein modification process", "protein phosphorylation", "palmitoyl-(protein) hydrolase activity", "palmitoyl hydrolase activity", "phosphorylation"], "splitLine": {"show": false}}}, "detail": {"method": "ORA"}}, "plot0": {"type": "chart", "snap": {"xAxis": {"boundaryGap": [0, 0.01], "type": "value", "name": "-lg(p_bonferroni)", "lineColor": "transparent", "splitLine": {"show": false}}, "color": ["#F2F2F2"], "grid": {"bottom": "3%", "left": "3%", "containLabel": true, "right": "12%", "top": "5%"}, "series": [{"type": "bar", "data": [13.321281912243151, 11.556529137977249, 4.307572801910292, 4.307572801910292, 3.9213901653036336, 3.083141235300246, 3.083141235300246, 2.237863830098888], "name": "-lg(p_bonferroni)"}], "tooltip": {"axisPointer": {"type": "shadow"}, "trigger": "axis"}, "yAxis": {"type": "category", "data": ["catalytic activity", "transferase activity", "protein modification process", "cellular protein modification process", "protein phosphorylation", "palmitoyl-(protein) hydrolase activity", "palmitoyl hydrolase activity", "phosphorylation"], "splitLine": {"show": false}}}, "detail": {"method": "ORA"}}};

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

}