/**
 * Created by sheep on 2017/5/1.
 */
$.getJSON("data/test2.json",function(result){
    console.log("main");
    init(result);
});

function init(data) {
    // plot type: Cytoscape or Echarts
    var type = data.type;
    console.log(type);
    if (type == 'cy') {
        init_cy(data.options);
    } else if (type == 'echarts') {
        init_echarts(data.options)
    } else if (type == 'viva') {
        init_viva_svg(data.options);
    }
}

function level_color(level) {
    level = parseInt(level);
    if (level == 0){
        return 0xff0000;
    }else if(level == 1){
        return 0xffff00;
    }else{
        return 0x111111 * (10 - level);
    }
}

function init_viva_svg(config) {
    console.log(config);
    var graph = Viva.Graph.graph();
    var exist = [];
    for (var i in config.elements){
        // console.log(config.elements[i].group);
        if(config.elements[i].group == 'edges'){
            // console.log(i);
            graph.addLink(config.elements[i].data.source, config.elements[i].data.target);
        }else{
            var level = parseInt(config.elements[i].data.level);
            // if (level > 4){ continue }
            graph.addNode(config.elements[i].data.label);
            // exist.push(config.elements[i].data.label);
        }
    }
    var layout = Viva.Graph.Layout.forceDirected(graph, {
        stableThreshold: 0.009,
        springLength : 5,
        springCoeff : 0.0002,
        dragCoeff : 0.02,
        gravity : -1.5
    });

    var graphics = Viva.Graph.View.svgGraphics();

    var colors = [
                        "#1f77b4", "#aec7e8",
                        "#ff7f0e", "#ffbb78",
                        "#2ca02c", "#98df8a",
                        "#d62728", "#ff9896",
                        "#9467bd", "#c5b0d5",
                        "#8c564b", "#c49c94",
                        "#e377c2", "#f7b6d2",
                        "#7f7f7f", "#c7c7c7",
                        "#bcbd22", "#dbdb8d",
                        "#17becf", "#9edae5"
                        ];


    graphics.node(function(node){
                        var circle = Viva.Graph.svg('circle')
                            .attr('r', 7)
                            .attr('stroke', '#fff')
                            .attr('stroke-width', '1.5px')
                            .attr("fill", colors[Math.round(Math.random() * colors.length)]);

                        // circle.append('title').text(node.data.label);

                        return circle;

                    }).placeNode(function(nodeUI, pos){
                        nodeUI.attr( "cx", pos.x).attr("cy", pos.y);
                    });

                    graphics.link(function(link){
                        return Viva.Graph.svg('line')
                                .attr('stroke', '#999')
                                .attr('stroke-width', Math.sqrt(link.data));
                    });

    var renderer = Viva.Graph.View.renderer(graph,
        {container: document.getElementById('cy'),
        graphics: graphics,
        layout: layout});
    renderer.run();
    setTimeout(function() {
        renderer.pause();
    }, 5000);
}

function init_viva(config){
    console.log(config);
    var graph = Viva.Graph.graph();
    var exist = [];
    // Step 2. We add nodes and edges to the graph:
    for (var i in config.elements){
        // console.log(config.elements[i].group);
        if(config.elements[i].group == undefined){
            // console.log(i);
            // graph.addLink(config.elements[i].data.source, config.elements[i].data.target);
        }else{
            var level = parseInt(config.elements[i].data.level);
            if (level > 4){ continue }
            console.log((11 - level));
            graph.addNode(config.elements[i].data.label, {size:
                (10 - parseInt(config.elements[i].data.level)) * (10 - parseInt(config.elements[i].data.level)) / 3,
                color: level_color(config.elements[i].data.level)});
            exist.push(config.elements[i].data.label);
        }
    }
    for (var i in config.elements){
        // console.log(config.elements[i].group);
        if(config.elements[i].group == undefined){
            var source = config.elements[i].data.source;
            var target = config.elements[i].data.target;
            if (exist.indexOf(source) >=0  && exist.indexOf(target) >=0){
                graph.addLink(config.elements[i].data.source, config.elements[i].data.target);
            }
            // console.log(i);
        }
    }

    var layout = Viva.Graph.Layout.forceDirected(graph, {
        stableThreshold: 0.009,
        springLength : 5,
        springCoeff : 0.0002,
        dragCoeff : 0.02,
        gravity : -1.5
    });

    var graphics = Viva.Graph.View.webglGraphics();

    var circleNode = buildCircleNodeShader();
    graphics.setNodeProgram(circleNode);

    graphics.node(function (node) {
        return new WebglCircle(node.data.size, node.data.color);
    });


    // Step 3. Render the graph.
    var renderer = Viva.Graph.View.renderer(graph,
        {container: document.getElementById('cy'),
        graphics: graphics,
        layout: layout});
    renderer.run();
}

function init_cy(config) {
    console.log(config);
    config.container = document.getElementById('cy');
    var cy = cytoscape(config);
    var defaults = {
        menuRadius: 100, // the radius of the circular menu in pixels
        selector: 'node', // elements matching this Cytoscape.js selector will trigger cxtmenus
        commands: [ // an array of commands to list in the menu or a function that returns the array
             { // example command
             fillColor: 'rgba(20, 20, 20, 0.75)', // optional: custom background color for item
             content: 'Detail', // html/text content to be displayed in the menu
             select: function(ele){ // a function to execute when the command is selected
             console.log( ele.id() ); // `ele` holds the reference to the active element
             }
             },
            { // example command
                fillColor: 'rgba(20, 20, 20, 0.75)', // optional: custom background color for item
                content: 'Expend', // html/text content to be displayed in the menu
                select: function(ele){ // a function to execute when the command is selected
                    console.log( ele.id() ); // `ele` holds the reference to the active element
                }
            },
            { // example command
                fillColor: 'rgba(20, 20, 20, 0.75)', // optional: custom background color for item
                content: 'Mark', // html/text content to be displayed in the menu
                select: function(ele){ // a function to execute when the command is selected
                    console.log( ele.id() ); // `ele` holds the reference to the active element
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

}

function init_echarts() {
    console.log("init echarts");
}

function register_event(cy) {
    cy.on('tap', 'node', function (evt) {
        console.log('tap at' + evt.target);
    })
}

function WebglCircle(size, color) {
    this.size = size;
    this.color = color;
}

// Next comes the hard part - implementation of API for custom shader
// program, used by webgl renderer:
function buildCircleNodeShader() {
    // For each primitive we need 4 attributes: x, y, color and size.
    var ATTRIBUTES_PER_PRIMITIVE = 4,
        nodesFS = [
            'precision mediump float;',
            'varying vec4 color;',

            'void main(void) {',
            '   if ((gl_PointCoord.x - 0.5) * (gl_PointCoord.x - 0.5) + (gl_PointCoord.y - 0.5) * (gl_PointCoord.y - 0.5) < 0.25) {',
            '     gl_FragColor = color;',
            '   } else {',
            '     gl_FragColor = vec4(0);',
            '   }',
            '}'].join('\n'),
        nodesVS = [
            'attribute vec2 a_vertexPos;',
            // Pack color and size into vector. First elemnt is color, second - size.
            // Since it's floating point we can only use 24 bit to pack colors...
            // thus alpha channel is dropped, and is always assumed to be 1.
            'attribute vec2 a_customAttributes;',
            'uniform vec2 u_screenSize;',
            'uniform mat4 u_transform;',
            'varying vec4 color;',

            'void main(void) {',
            '   gl_Position = u_transform * vec4(a_vertexPos/u_screenSize, 0, 1);',
            '   gl_PointSize = a_customAttributes[1] * u_transform[0][0];',
            '   float c = a_customAttributes[0];',
            '   color.b = mod(c, 256.0); c = floor(c/256.0);',
            '   color.g = mod(c, 256.0); c = floor(c/256.0);',
            '   color.r = mod(c, 256.0); c = floor(c/256.0); color /= 255.0;',
            '   color.a = 1.0;',
            '}'].join('\n');

    var program,
        gl,
        buffer,
        locations,
        utils,
        nodes = new Float32Array(64),
        nodesCount = 0,
        canvasWidth, canvasHeight, transform,
        isCanvasDirty;

    return {
        /**
         * Called by webgl renderer to load the shader into gl context.
         */
        load : function (glContext) {
            gl = glContext;
            webglUtils = Viva.Graph.webgl(glContext);

            program = webglUtils.createProgram(nodesVS, nodesFS);
            gl.useProgram(program);
            locations = webglUtils.getLocations(program, ['a_vertexPos', 'a_customAttributes', 'u_screenSize', 'u_transform']);

            gl.enableVertexAttribArray(locations.vertexPos);
            gl.enableVertexAttribArray(locations.customAttributes);

            buffer = gl.createBuffer();
        },

        /**
         * Called by webgl renderer to update node position in the buffer array
         *
         * @param nodeUI - data model for the rendered node (WebGLCircle in this case)
         * @param pos - {x, y} coordinates of the node.
         */
        position : function (nodeUI, pos) {
            var idx = nodeUI.id;
            nodes[idx * ATTRIBUTES_PER_PRIMITIVE] = pos.x;
            nodes[idx * ATTRIBUTES_PER_PRIMITIVE + 1] = -pos.y;
            nodes[idx * ATTRIBUTES_PER_PRIMITIVE + 2] = nodeUI.color;
            nodes[idx * ATTRIBUTES_PER_PRIMITIVE + 3] = nodeUI.size;
        },

        /**
         * Request from webgl renderer to actually draw our stuff into the
         * gl context. This is the core of our shader.
         */
        render : function() {
            gl.useProgram(program);
            gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
            gl.bufferData(gl.ARRAY_BUFFER, nodes, gl.DYNAMIC_DRAW);

            if (isCanvasDirty) {
                isCanvasDirty = false;
                gl.uniformMatrix4fv(locations.transform, false, transform);
                gl.uniform2f(locations.screenSize, canvasWidth, canvasHeight);
            }

            gl.vertexAttribPointer(locations.vertexPos, 2, gl.FLOAT, false, ATTRIBUTES_PER_PRIMITIVE * Float32Array.BYTES_PER_ELEMENT, 0);
            gl.vertexAttribPointer(locations.customAttributes, 2, gl.FLOAT, false, ATTRIBUTES_PER_PRIMITIVE * Float32Array.BYTES_PER_ELEMENT, 2 * 4);

            gl.drawArrays(gl.POINTS, 0, nodesCount);
        },

        /**
         * Called by webgl renderer when user scales/pans the canvas with nodes.
         */
        updateTransform : function (newTransform) {
            transform = newTransform;
            isCanvasDirty = true;
        },

        /**
         * Called by webgl renderer when user resizes the canvas with nodes.
         */
        updateSize : function (newCanvasWidth, newCanvasHeight) {
            canvasWidth = newCanvasWidth;
            canvasHeight = newCanvasHeight;
            isCanvasDirty = true;
        },

        /**
         * Called by webgl renderer to notify us that the new node was created in the graph
         */
        createNode : function (node) {
            nodes = webglUtils.extendArray(nodes, nodesCount, ATTRIBUTES_PER_PRIMITIVE);
            nodesCount += 1;
        },

        /**
         * Called by webgl renderer to notify us that the node was removed from the graph
         */
        removeNode : function (node) {
            if (nodesCount > 0) { nodesCount -=1; }

            if (node.id < nodesCount && nodesCount > 0) {
                // we do not really delete anything from the buffer.
                // Instead we swap deleted node with the "last" node in the
                // buffer and decrease marker of the "last" node. Gives nice O(1)
                // performance, but make code slightly harder than it could be:
                webglUtils.copyArrayPart(nodes, node.id*ATTRIBUTES_PER_PRIMITIVE, nodesCount*ATTRIBUTES_PER_PRIMITIVE, ATTRIBUTES_PER_PRIMITIVE);
            }
        },

        /**
         * This method is called by webgl renderer when it changes parts of its
         * buffers. We don't use it here, but it's needed by API (see the comment
         * in the removeNode() method)
         */
        replaceProperties : function(replacedNode, newNode) {},
    };
}