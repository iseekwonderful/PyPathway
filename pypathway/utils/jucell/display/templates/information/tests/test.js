/**
 * Created by sheep on 2017/4/26.
 */

var json_data = '';

$.getJSON('data.json', function(json) {
    document.getElementById('var_name').value = json.data['a'];
    document.getElementById('var_value').value = json.data['b'];
    json_data = json
});

function call_back(dict) {
    json_data.data['a'] = document.getElementById('var_name').value;
    json_data.data['b'] = document.getElementById('var_value').value;
    var kernel = parent.IPython.notebook.kernel;
    console.log(json_data['call_back'] + '(' + JSON.stringify(json_data.data) + ')');
    kernel.execute(json_data['call_back'] + '(' + JSON.stringify(json_data.data) + ')');
}
