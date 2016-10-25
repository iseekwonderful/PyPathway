var sbgnStyleSheet = cytoscape.stylesheet()
        .selector("node")
        .css({
          'border-width': 1.5,
          'border-color': '#555',
          'background-color': '#f6f6f6',
          'font-size': 11,
//          'shape': 'data(sbgnclass)',
          'background-opacity': 0.5,
          'text-opacity': 1,
          'opacity': 1
        })
        .selector("node[?sbgnclonemarker][sbgnclass='perturbing agent']")
        .css({
          'background-image': 'sampleapp-images/clone_bg.png',
          'background-position-x': '50%',
          'background-position-y': '100%',
          'background-width': '100%',
          'background-height': '25%',
          'background-fit': 'none',
          'background-image-opacity': function (ele) {
            if(!ele.data('sbgnclonemarker')){
              return 0;
            }
            return ele._private.style['background-opacity'].value;
          }
        })
        .selector("node[sbgnclass][sbgnclass!='complex'][sbgnclass!='process'][sbgnclass!='association'][sbgnclass!='dissociation'][sbgnclass!='compartment'][sbgnclass!='source and sink']")
        .css({
//          'content': 'data(sbgnlabel)',
          'content': function (ele) {
            return getElementContent(ele);
          },
          'text-valign': 'center',
          'text-halign': 'center',
          'font-size': function (ele) {
            return getLabelTextSize(ele);
          }
        })
        .selector("node[sbgnclass]")
        .css({
          'shape': function (ele) {
            return getCyShape(ele);
          }
        })
        .selector("node[sbgnclass='perturbing agent']")
        .css({
          'shape-polygon-points': '-1, -1,   -0.5, 0,  -1, 1,   1, 1,   0.5, 0, 1, -1'
        })
        .selector("node[sbgnclass='association']")
        .css({
          'background-color': '#6B6B6B'
        })
        .selector("node[sbgnclass='tag']")
        .css({
          'shape-polygon-points': '-1, -1,   0.25, -1,   1, 0,    0.25, 1,    -1, 1'
        })
        .selector("node[sbgnclass='complex']")
        .css({
          'background-color': '#F4F3EE',
          'text-valign': 'bottom',
          'text-halign': 'center',
          'font-size': function (ele) {
            return getLabelTextSize(ele);
          },
          'width': function(ele){
            if(ele.children() == null || ele.children().length == 0){
              return '36';
            }
            return ele.data('width');
          },
          'height': function(ele){
            if(ele.children() == null || ele.children().length == 0){
              return '36';
            }
            return ele.data('height');
          },
          'content': function(ele){
            return getElementContent(ele);
          }
        })
        .selector("node[sbgnclass='compartment']")
        .css({
          'border-width': 3.75,
          'background-opacity': 0,
          'background-color': '#FFFFFF',
          'content': function(ele){
            return getElementContent(ele);
          },
          'width': function(ele){
            if(ele.children() == null || ele.children().length == 0){
              return '36';
            }
            return ele.data('width');
          },
          'height': function(ele){
            if(ele.children() == null || ele.children().length == 0){
              return '36';
            }
            return ele.data('height');
          },
          'text-valign': 'bottom',
          'text-halign': 'center',
          'font-size': function (ele) {
            return getLabelTextSize(ele);
          }
        })
        .selector("node[sbgnclass][sbgnclass!='complex'][sbgnclass!='compartment'][sbgnclass!='submap']")
        .css({
          'width': 'data(sbgnbbox.w)',
          'height': 'data(sbgnbbox.h)'
        })
        .selector("node:selected")
        .css({
          'border-color': '#d67614',
          'target-arrow-color': '#000',
          'text-outline-color': '#000'})
        .selector("node:active")
        .css({
          'background-opacity': 0.7, 'overlay-color': '#d67614',
          'overlay-padding': '14'
        })
        .selector("edge")
        .css({
          'curve-style': 'bezier',
          'line-color': '#555',
          'target-arrow-fill': 'hollow',
          'source-arrow-fill': 'hollow',
          'width': 1.5,
          'target-arrow-color': '#555',
          'source-arrow-color': '#555',
//          'target-arrow-shape': 'data(sbgnclass)'
        })
        .selector("edge[sbgnclass]")
        .css({
          'target-arrow-shape': function (ele) {
            return getCyArrowShape(ele);
          },
          'source-arrow-shape': 'none'
        })
        .selector("edge[sbgnclass='inhibition']")
        .css({
          'target-arrow-fill': 'filled'
        })
        .selector("edge[sbgnclass='consumption']")
        .css({
          'line-style': 'consumption'
        })
        .selector("edge[sbgnclass='production']")
        .css({
          'target-arrow-fill': 'filled',
          'line-style': 'production'
        })
        .selector("edge:selected")
        .css({
          'line-color': '#d67614',
          'source-arrow-color': '#d67614',
          'target-arrow-color': '#d67614'
        })
        .selector("edge:active")
        .css({
          'background-opacity': 0.7, 'overlay-color': '#d67614',
          'overlay-padding': '8'
        })
        .selector("core")
        .css({
          'selection-box-color': '#d67614',
          'selection-box-opacity': '0.2', 'selection-box-border-color': '#d67614'
        })
        .selector(".ui-cytoscape-edgehandles-source")
        .css({
          'border-color': '#5CC2ED',
          'border-width': 3
        })
        .selector(".ui-cytoscape-edgehandles-target, node.ui-cytoscape-edgehandles-preview")
        .css({
          'background-color': '#5CC2ED'
        })
        .selector("edge.ui-cytoscape-edgehandles-preview")
        .css({
          'line-color': '#5CC2ED'
        })
        .selector("node.ui-cytoscape-edgehandles-preview, node.intermediate")
        .css({
          'shape': 'rectangle',
          'width': 15,
          'height': 15
        })
        .selector('edge.not-highlighted')
        .css({
          'opacity': 0.3,
          'text-opacity': 0.3,
          'background-opacity': 0.3
        })
        .selector('node.not-highlighted')
        .css({
          'border-opacity': 0.3,
          'text-opacity': 0.3,
          'background-opacity': 0.3
        })
        .selector('edge.meta')
        .css({
          'line-color': '#C4C4C4',
          'source-arrow-color': '#C4C4C4',
          'target-arrow-color': '#C4C4C4'
        })
        .selector("edge.meta:selected")
        .css({
          'line-color': '#d67614',
          'source-arrow-color': '#d67614',
          'target-arrow-color': '#d67614'
        })
        .selector("node.changeBackgroundOpacity")
        .css({
          'background-opacity': 'data(backgroundOpacity)'
        })
        .selector("node.changeLabelTextSize")
        .css({
          'font-size': function (ele) {
            return getLabelTextSize(ele);
          }
        })
        .selector("node.changeContent")
        .css({
          'content': function (ele) {
            return getElementContent(ele);
          }
        })
        .selector("node.changeBorderColor")
        .css({
          'border-color': 'data(borderColor)'
        })
        .selector("node.changeBorderColor:selected")
        .css({
          'border-color': '#d67614'
        })
        .selector("edge.changeLineColor")
        .css({
          'line-color': 'data(lineColor)',
          'source-arrow-color': 'data(lineColor)',
          'target-arrow-color': 'data(lineColor)'
        })
        .selector("edge.changeLineColor:selected")
        .css({
          'line-color': '#d67614',
          'source-arrow-color': '#d67614',
          'target-arrow-color': '#d67614'
        })
        .selector('edge.changeLineColor.meta')
        .css({
          'line-color': '#C4C4C4',
          'source-arrow-color': '#C4C4C4',
          'target-arrow-color': '#C4C4C4'
        })
        .selector("edge.changeLineColor.meta:selected")
        .css({
          'line-color': '#d67614',
          'source-arrow-color': '#d67614',
          'target-arrow-color': '#d67614'
        }).selector("node.changeClonedStatus")
        .css({
          'background-image-opacity': function (ele) {
            if(!ele.data('sbgnclonemarker')){
              return 0;
            }
            return ele._private.style['background-opacity'].value;
          }
        });
// end of sbgnStyleSheet

var NotyView = Backbone.View.extend({
  render: function () {
    //this.model["theme"] = " twitter bootstrap";
    this.model["layout"] = "bottomRight";
    this.model["timeout"] = 8000;
    this.model["text"] = "Right click on a gene to see its details!";

    noty(this.model);
    return this;
  }
});

var SBGNContainer = Backbone.View.extend({
  cyStyle: sbgnStyleSheet,
  render: function () {
    // (new NotyView({
    //   template: "#noty-info",
    //   model: {}
    // })).render();

    var container = $(this.el);
    // container.html("");
    // container.append(_.template($("#loading-template").html()));


    var cytoscapeJsGraph = (this.model.cytoscapeJsGraph);

    var positionMap = {};
    //add position information to data for preset layout
    for (var i = 0; i < cytoscapeJsGraph.nodes.length; i++) {
      var xPos = cytoscapeJsGraph.nodes[i].data.sbgnbbox.x;
      var yPos = cytoscapeJsGraph.nodes[i].data.sbgnbbox.y;
      positionMap[cytoscapeJsGraph.nodes[i].data.id] = {'x': xPos, 'y': yPos};
    }

    var cyOptions = {
      elements: cytoscapeJsGraph,
      style: sbgnStyleSheet,
      layout: {
        name: 'preset',
        positions: positionMap
      },
      showOverlay: false, minZoom: 0.125, maxZoom: 16,
      boxSelectionEnabled: true,
      motionBlur: true,
      wheelSensitivity: 0.1,
      ready: function ()
      {
        window.cy = this;
        cy.nodes().addClass('changeLabelTextSize');
        
        registerUndoRedoActions();
        
        // register the extensions
        
        cy.expandCollapse(getExpandCollapseOptions());
        
        cy.contextMenus({
          menuItemClasses: ['customized-context-menus-menu-item']
        });
        
        cy.edgeBendEditing({
          // this function specifies the positions of bend points
          bendPositionsFunction: function(ele) {
            return ele.data('bendPointPositions');
          },
          // whether the bend editing operations are undoable (requires cytoscape-undo-redo.js)
          undoable: true,
          // title of remove bend point menu item
          removeBendMenuItemTitle: "Delete Bend Point"
        });
        
        cy.appendMenuItems([
          {
            id: 'ctx-menu-sbgn-properties',
            title: 'Properties...',
            coreAsWell: true,
            onClickFunction: function (event) { 
              $("#sbgn-properties").trigger("click");
            }
          },
          {
            id: 'ctx-menu-delete',
            title: 'Delete',
            selector: 'node, edge', 
            onClickFunction: function (event) { 
              cy.undoRedo().do("removeEles", event.cyTarget);
            }
          },
          {
            id: 'ctx-menu-delete-selected', 
            title: 'Delete Selected', 
            onClickFunction: function () { 
              $("#delete-selected-simple").trigger('click');
            },
            coreAsWell: true // Whether core instance have this item on cxttap
          },
          {
            id: 'ctx-menu-hide-selected', 
            title: 'Hide Selected', 
            onClickFunction: function () { 
              $("#hide-selected").trigger('click');
            },
            coreAsWell: true // Whether core instance have this item on cxttap
          },
          {
            id: 'ctx-menu-show-all', 
            title: 'Show All', 
            onClickFunction: function () { 
              $("#show-all").trigger('click');
            },
            coreAsWell: true // Whether core instance have this item on cxttap
          },
          {
            id: 'ctx-menu-expand', // ID of menu item
            title: 'Expand', // Title of menu item
            // Filters the elements to have this menu item on cxttap
            // If the selector is not truthy no elements will have this menu item on cxttap
            selector: 'node[expanded-collapsed="collapsed"]', 
            onClickFunction: function (event) { // The function to be executed on click
              cy.undoRedo().do("expand", {
                nodes: event.cyTarget
              });
            }
          },
          {
            id: 'ctx-menu-collapse',
            title: 'Collapse',
            selector: 'node[expanded-collapsed="expanded"]', 
            onClickFunction: function (event) {
              cy.undoRedo().do("collapse", {
                nodes: event.cyTarget
              });
            }
          },
          {
            id: 'ctx-menu-perform-layout', 
            title: 'Perform Layout', 
            onClickFunction: function () { 
              if (modeHandler.mode == "selection-mode") {
                $("#perform-layout").trigger('click');
              }
            },
            coreAsWell: true // Whether core instance have this item on cxttap
          },
          {
            id: 'ctx-menu-biogene-properties', 
            title: 'BioGene Properties', 
            selector: 'node[sbgnclass="macromolecule"],[sbgnclass="nucleic acid feature"],[sbgnclass="unspecified entity"]',
            onClickFunction: function (event) { 
              bioGeneQtip(event.cyTarget);
            }
          }
        ]);
        
        cy.clipboard({
          clipboardSize: 5, // Size of clipboard. 0 means unlimited. If size is exceeded, first added item in clipboard will be removed.
          shortcuts: {
            enabled: true, // Whether keyboard shortcuts are enabled
            undoable: true // and if undoRedo extension exists
          }
        });
        
        cy.viewUtilities({
          node: {
              highlighted: {}, // styles for when nodes are highlighted.
              unhighlighted: { // styles for when nodes are unhighlighted.
                'border-opacity': 0.3,
                'text-opacity': 0.3,
                'background-opacity': 0.3
              },
              hidden: {
                'display': 'none'
              }
            },
            edge: {
              highlighted: {}, // styles for when edges are highlighted.
              unhighlighted: { // styles for when edges are unhighlighted.
                'opacity': 0.3,
                'text-opacity': 0.3,
                'background-opacity': 0.3
              },
              hidden: {
                'display': 'none'
              }
            }
        });
        
        var edges = cy.edges();

        refreshPaddings();
        
        var panProps = ({
          fitPadding: 10,
          fitSelector: ':visible',
          animateOnFit: function(){
            return sbgnStyleRules['animate-on-drawing-changes'];
          },
          animateOnZoom: function(){
            return sbgnStyleRules['animate-on-drawing-changes'];
          }
        });
        
        container.cytoscapePanzoom(panProps);

        // listen events

        cy.on("beforeCollapse", "node", function (event) {
          var node = this;
          //The children info of complex nodes should be shown when they are collapsed
          if (node._private.data.sbgnclass == "complex") {
            //The node is being collapsed store infolabel to use it later
            var infoLabel = getInfoLabel(node);
            node._private.data.infoLabel = infoLabel;
          }
          
          var edges = cy.edges();
          
          // remove bend points before collapse
          for (var i = 0; i < edges.length; i++) {
            var edge = edges[i];
            if(edge.hasClass('edgebendediting-hasbendpoints')) {
              edge.removeClass('edgebendediting-hasbendpoints');
              delete edge._private.classes['edgebendediting-hasbendpoints'];
            }
          }
          
          edges.scratch('cyedgebendeditingWeights', []);
          edges.scratch('cyedgebendeditingDistances', []);
          
        });
        
        cy.on("afterCollapse", "node", function (event) {
          var node = this;
          refreshPaddings();

          if (node._private.data.sbgnclass == "complex") {
            node.addClass('changeContent');
          }
        });
        
        cy.on("beforeExpand", "node", function (event) {
          var node = this;
          node.removeData("infoLabel");
        });
        
        cy.on("afterExpand", "node", function (event) {
          var node = this;
          cy.nodes().updateCompoundBounds();

          //Don't show children info when the complex node is expanded
          if (node._private.data.sbgnclass == "complex") {
            node.removeStyle('content');
          }
          
          refreshPaddings();
        });

        cy.on("afterDo", function(actionName, args){
          refreshUndoRedoButtonsStatus();
        });

        cy.on("afterUndo", function(actionName, args){
          refreshUndoRedoButtonsStatus();
        });
        
        cy.on("afterRedo", function(actionName, args){
          refreshUndoRedoButtonsStatus();
        });

        // mouse click
        cy.on("mousedown", "node", function (event) {
          var self = this;
          // console.log("Down: " + event.cyTarget.id());
          if (modeHandler.mode == 'selection-mode' && window.ctrlKeyDown) {
            enableDragAndDropMode();
            window.nodeToDragAndDrop = self;
          }
        });

        cy.on("mouseup", function (event) {
          on_mouse_up(event);
          // console.log(event.cyTarget == cy);
          var self = event.cyTarget;
          if (window.dragAndDropModeEnabled) {
            var nodesData = getNodesData();
            nodesData.firstTime = true;
            var newParent;
            if (self != cy) {
              newParent = self;
            }
            var node = window.nodeToDragAndDrop;

            if (newParent && self.data("sbgnclass") != "complex" && self.data("sbgnclass") != "compartment") {
              return;
            }

            if (newParent && self.data("sbgnclass") == "complex" && !isEPNClass(node.data("sbgnclass"))) {
              return;
            }

            disableDragAndDropMode();
            
            if (node.parent()[0] == newParent || node._private.data.parent == node.id()) {
              return;
            }
            
            var param = {
              newParent: newParent,
              node: node,
              nodesData: nodesData,
              posX: event.cyPosition.x,
              posY: event.cyPosition.y
            };
            
            cy.undoRedo().do("changeParent", param);
          }
        });

        cy.on('mouseover',/*'node',*/ function (event) {
          on_mouse_over(event);
          return;
          if (event.cyTarget == cy || !event.cyTarget.isNode()){
            return;
          }
          var node = this;

          $(".qtip").remove();

          if (event.originalEvent.shiftKey)
            return;

          // node.qtipTimeOutFcn = setTimeout(function () {
          //   nodeQtipFunction(node);
          // }, 1000);
        });

        cy.on('mouseout',/* 'node', */function (event) {
          on_mouse_out(event);
          if (event.cyTarget == cy || !event.cyTarget.isNode()){
            return;
          }
          if (this.qtipTimeOutFcn != null) {
            clearTimeout(this.qtipTimeOutFcn);
            this.qtipTimeOutFcn = null;
          }
          this.mouseover = false;           //make preset layout to redraw the nodes
          cy.forceRender();
        });

        window.firstSelectedNode = null;
        cy.on('select', 'node', function (event) {
          // console.log("select");
          if (cy.nodes(':selected').filter(':visible').length == 1) {
            window.firstSelectedNode = this;
          }
        });

        cy.on('unselect', 'node', function (event) {
          // console.log("unselect");
          if (window.firstSelectedNode == this) {
            window.firstSelectedNode = null;
          }
        });

        cy.on('tap', function (event) {
          $('input').blur();
        });

        cy.on('tap', 'node', function (event) {
          var node = this;

          on_mouse_down(event);

          return;
          //$(".qtip").remove();

          if (event.originalEvent.shiftKey)
            return;

          if (node.qtipTimeOutFcn != null) {
            clearTimeout(node.qtipTimeOutFcn);
            node.qtipTimeOutFcn = null;
          }

          //nodeQtipFunction(node);

        });
      }
    };
    container.html("");
    container.cy(cyOptions);
    // // change value here
    // console.log("init hook");
    // value_change_hook();
    return this;
  }
});

var SBGNLayout = Backbone.View.extend({
  defaultLayoutProperties: {
    name: 'cose-bilkent',
    nodeRepulsion: 4500,
    nodeOverlap: 10,
    idealEdgeLength: 50,
    edgeElasticity: 0.45,
    nestingFactor: 0.1,
    gravity: 0.25,
    numIter: 2500,
    tile: true,
    animationEasing: 'cubic-bezier(0.19, 1, 0.22, 1)',
    animate: 'end',
    animationDuration: 1000,
    randomize: true,
    tilingPaddingVertical: function () {
      return calculateTilingPaddings(parseInt(sbgnStyleRules['tiling-padding-vertical'], 10));
    },
    tilingPaddingHorizontal: function () {
      return calculateTilingPaddings(parseInt(sbgnStyleRules['tiling-padding-horizontal'], 10));
    },
    gravityRangeCompound: 1.5,
    gravityCompound: 1.0,
    gravityRange: 3.8,
    stop: function(){
      if($('.layout-spinner').length > 0){
        $('.layout-spinner').remove();
      }
    }
  },
  currentLayoutProperties: null,
  initialize: function () {
    var self = this;
    self.copyProperties();

    var templateProperties = _.clone(self.currentLayoutProperties);
    templateProperties.tilingPaddingVertical = sbgnStyleRules['tiling-padding-vertical'];
    templateProperties.tilingPaddingHorizontal = sbgnStyleRules['tiling-padding-horizontal'];

    self.template = _.template($("#layout-settings-template").html(), templateProperties);
  },
  copyProperties: function () {
    this.currentLayoutProperties = _.clone(this.defaultLayoutProperties);
  },
  applyLayout: function (preferences, undoable) {
    if(preferences === undefined){
      preferences = {};
    }
    var options = $.extend({}, this.currentLayoutProperties, preferences);
    if(undoable === false) {
      cy.elements().filter(':visible').layout(options);
    }
    else {
      cy.undoRedo().do("layout", {
        options: options,
        eles: cy.elements().filter(':visible')
      });
    }
  },
  render: function () {
    var self = this;

    var templateProperties = _.clone(self.currentLayoutProperties);
    templateProperties.tilingPaddingVertical = sbgnStyleRules['tiling-padding-vertical'];
    templateProperties.tilingPaddingHorizontal = sbgnStyleRules['tiling-padding-horizontal'];

    self.template = _.template($("#layout-settings-template").html(), templateProperties);
    $(self.el).html(self.template);

    $(self.el).dialog();

    $("#save-layout").die("click").live("click", function (evt) {
      self.currentLayoutProperties.nodeRepulsion = Number(document.getElementById("node-repulsion").value);
      self.currentLayoutProperties.nodeOverlap = Number(document.getElementById("node-overlap").value);
      self.currentLayoutProperties.idealEdgeLength = Number(document.getElementById("ideal-edge-length").value);
      self.currentLayoutProperties.edgeElasticity = Number(document.getElementById("edge-elasticity").value);
      self.currentLayoutProperties.nestingFactor = Number(document.getElementById("nesting-factor").value);
      self.currentLayoutProperties.gravity = Number(document.getElementById("gravity").value);
      self.currentLayoutProperties.numIter = Number(document.getElementById("num-iter").value);
      self.currentLayoutProperties.tile = document.getElementById("tile").checked;
      self.currentLayoutProperties.animate = document.getElementById("animate").checked?'during':'end';
      self.currentLayoutProperties.randomize = !document.getElementById("incremental").checked;
      self.currentLayoutProperties.gravityRangeCompound = Number(document.getElementById("gravity-range-compound").value);
      self.currentLayoutProperties.gravityCompound = Number(document.getElementById("gravity-compound").value);
      self.currentLayoutProperties.gravityRange = Number(document.getElementById("gravity-range").value);

      sbgnStyleRules['tiling-padding-vertical'] = Number(document.getElementById("tiling-padding-vertical").value);
      sbgnStyleRules['tiling-padding-horizontal'] = Number(document.getElementById("tiling-padding-horizontal").value);

      $(self.el).dialog('close');
    });

    $("#default-layout").die("click").live("click", function (evt) {
      self.copyProperties();

      sbgnStyleRules['tiling-padding-vertical'] = defaultSbgnStyleRules['tiling-padding-vertical'];
      sbgnStyleRules['tiling-padding-horizontal'] = defaultSbgnStyleRules['tiling-padding-horizontal'];

      var templateProperties = _.clone(self.currentLayoutProperties);
      templateProperties.tilingPaddingVertical = sbgnStyleRules['tiling-padding-vertical'];
      templateProperties.tilingPaddingHorizontal = sbgnStyleRules['tiling-padding-horizontal'];

      self.template = _.template($("#layout-settings-template").html(), templateProperties);
      $(self.el).html(self.template);
    });

    return this;
  }
});

var SBGNProperties = Backbone.View.extend({
  defaultSBGNProperties: {
    compoundPadding: parseInt(sbgnStyleRules['compound-padding'], 10),
    dynamicLabelSize: sbgnStyleRules['dynamic-label-size'],
    fitLabelsToNodes: sbgnStyleRules['fit-labels-to-nodes'],
    rearrangeAfterExpandCollapse: sbgnStyleRules['rearrange-after-expand-collapse'],
    animateOnDrawingChanges: sbgnStyleRules['animate-on-drawing-changes']
  },
  currentSBGNProperties: null,
  initialize: function () {
    var self = this;
    self.copyProperties();
    self.template = _.template($("#sbgn-properties-template").html(), self.currentSBGNProperties);
  },
  copyProperties: function () {
    this.currentSBGNProperties = _.clone(this.defaultSBGNProperties);
  },
  render: function () {
    var self = this;
    self.template = _.template($("#sbgn-properties-template").html(), self.currentSBGNProperties);
    $(self.el).html(self.template);

    $(self.el).dialog();

    $("#save-sbgn").die("click").live("click", function (evt) {

      var param = {};
      param.firstTime = true;
      param.previousSBGNProperties = _.clone(self.currentSBGNProperties);

      self.currentSBGNProperties.compoundPadding = Number(document.getElementById("compound-padding").value);
      self.currentSBGNProperties.dynamicLabelSize = $('select[name="dynamic-label-size"] option:selected').val();
      self.currentSBGNProperties.fitLabelsToNodes = document.getElementById("fit-labels-to-nodes").checked;
      self.currentSBGNProperties.rearrangeAfterExpandCollapse =
          document.getElementById("rearrange-after-expand-collapse").checked;
      self.currentSBGNProperties.animateOnDrawingChanges =
          document.getElementById("animate-on-drawing-changes").checked;

      //Refresh paddings if needed
      if (sbgnStyleRules['compound-padding'] != self.currentSBGNProperties.compoundPadding) {
        sbgnStyleRules['compound-padding'] = self.currentSBGNProperties.compoundPadding;
        refreshPaddings();
      }
      //Refresh label size if needed
      if (sbgnStyleRules['dynamic-label-size'] != self.currentSBGNProperties.dynamicLabelSize) {
        sbgnStyleRules['dynamic-label-size'] = '' + self.currentSBGNProperties.dynamicLabelSize;
        cy.nodes().removeClass('changeLabelTextSize');
        cy.nodes().addClass('changeLabelTextSize');
      }
      //Refresh truncations if needed
      if (sbgnStyleRules['fit-labels-to-nodes'] != self.currentSBGNProperties.fitLabelsToNodes) {
        sbgnStyleRules['fit-labels-to-nodes'] = self.currentSBGNProperties.fitLabelsToNodes;
        cy.nodes().removeClass('changeContent');
        cy.nodes().addClass('changeContent');
      }

      sbgnStyleRules['rearrange-after-expand-collapse'] = 
              self.currentSBGNProperties.rearrangeAfterExpandCollapse;
      
      sbgnStyleRules['animate-on-drawing-changes'] = 
              self.currentSBGNProperties.animateOnDrawingChanges;

      $(self.el).dialog('close');
    });

    $("#default-sbgn").die("click").live("click", function (evt) {
      self.copyProperties();
      self.template = _.template($("#sbgn-properties-template").html(), self.currentSBGNProperties);
      $(self.el).html(self.template);
    });

    return this;
  }
});

var PathsBetweenQuery = Backbone.View.extend({
  defaultQueryParameters: {
    geneSymbols: "",
    lengthLimit: 1
//    shortestK: 0,
//    enableShortestKAlteration: false,
//    ignoreS2SandT2TTargets: false
  },
  currentQueryParameters: null,
  initialize: function () {
    var self = this;
    self.copyProperties();
    self.template = _.template($("#query-pathsbetween-template").html(), self.currentQueryParameters);
  },
  copyProperties: function () {
    this.currentQueryParameters = _.clone(this.defaultQueryParameters);
  },
  render: function () {
    var self = this;
    self.template = _.template($("#query-pathsbetween-template").html(), self.currentQueryParameters);
    $(self.el).html(self.template);

    $("#query-pathsbetween-enable-shortest-k-alteration").change(function(e){
      if(document.getElementById("query-pathsbetween-enable-shortest-k-alteration").checked){
        $( "#query-pathsbetween-shortest-k" ).prop( "disabled", false );
      }
      else {
        $( "#query-pathsbetween-shortest-k" ).prop( "disabled", true );
      }
    });

    $(self.el).dialog({width:'auto'});

    $("#save-query-pathsbetween").die("click").live("click", function (evt) {

      self.currentQueryParameters.geneSymbols = document.getElementById("query-pathsbetween-gene-symbols").value;
      self.currentQueryParameters.lengthLimit = Number(document.getElementById("query-pathsbetween-length-limit").value);
//      self.currentQueryParameters.shortestK = Number(document.getElementById("query-pathsbetween-shortest-k").value);
//      self.currentQueryParameters.enableShortestKAlteration =
//              document.getElementById("query-pathsbetween-enable-shortest-k-alteration").checked;
//      self.currentQueryParameters.ignoreS2SandT2TTargets =
//              document.getElementById("query-pathsbetween-ignore-s2s-t2t-targets").checked;
      
      var pc2URL = "http://www.pathwaycommons.org/pc2/";
      var format = "graph?format=SBGN";
      var kind = "&kind=PATHSBETWEEN";
      var limit = "&limit=" + self.currentQueryParameters.lengthLimit;
      var sources = "";
      var newfilename = "";
      
      var geneSymbolsArray = self.currentQueryParameters.geneSymbols.replace("\n"," ").replace("\t"," ").split(" ");
      for(var i = 0; i < geneSymbolsArray.length; i++){
        var currentGeneSymbol = geneSymbolsArray[i];
        if(currentGeneSymbol.length == 0 || currentGeneSymbol == ' ' || currentGeneSymbol == '\n' || currentGeneSymbol == '\t'){
          continue;
        }
        
        sources = sources + "&source=" + currentGeneSymbol;
        
        if(newfilename == ''){
          newfilename = currentGeneSymbol;
        }
        else{
          newfilename = newfilename + '_' + currentGeneSymbol;
        }
      }
      
      newfilename = newfilename + '_PBTWN.sbgnml';
      
      setFileContent(newfilename);
      pc2URL = pc2URL + format + kind + limit + sources;
      
      var containerWidth = cy.width();
      var containerHeight = cy.height();
      $('#sbgn-network-container').html('<i style="position: absolute; z-index: 9999999; left: ' + containerWidth / 2 + 'px; top: ' + containerHeight / 2 + 'px;" class="fa fa-spinner fa-spin fa-3x fa-fw"></i>');
      
      $.ajax(
      {
        url: pc2URL,
        type: 'GET',
        success: function(data)
        {
          (new SBGNContainer({
            el: '#sbgn-network-container',
            model: {cytoscapeJsGraph: sbgnmlToJson.convert(data)}
          })).render();
          inspectorUtilities.handleSBGNInspector();
        }
      });
      
      $(self.el).dialog('close');
    });
    
    $("#cancel-query-pathsbetween").die("click").live("click", function (evt) {
      $(self.el).dialog('close');
    });
    
    return this;
  }
});

var ReactionTemplate = Backbone.View.extend({
  defaultTemplateParameters: {
    templateType: "association",
    macromoleculeList: ["", ""],
    templateReactionEnableComplexName: true,
    templateReactionComplexName: "",
    getMacromoleculesHtml: function(){
      var html = "<table>";
      for( var i = 0; i < this.macromoleculeList.length; i++){
        html += "<tr><td>"
          + "<input type='text' class='template-reaction-textbox input-small layout-text' name='"
          + i + "'" + " value='" + this.macromoleculeList[i] + "'></input>"
          + "</td><td><img style='padding-bottom: 8px;' class='template-reaction-delete-button' width='12px' height='12px' name='" + i + "' src='sampleapp-images/delete.png'/></td></tr>"; 
      }
      
      html += "<tr><td><img id='template-reaction-add-button' src='sampleapp-images/add.png'/></td></tr></table>";
      return html;
    },
    getComplexHtml: function(){
      var html = "<table>"
        + "<tr><td><input type='checkbox' class='input-small layout-text' id='template-reaction-enable-complex-name'";
        
      if(this.templateReactionEnableComplexName){
        html += " checked ";
      }
        
      html += "/>"
        + "</td><td><input type='text' class='input-small layout-text' id='template-reaction-complex-name' value='" 
        + this.templateReactionComplexName + "'";
      
      if(!this.templateReactionEnableComplexName){
        html += " disabled ";
      }
      
      html += "></input>"
        + "</td></tr></table>";
        
      return html;
    },
    getInputHtml: function(){
      if(this.templateType === 'association') {
        return this.getMacromoleculesHtml();
      }
      else if(this.templateType === 'dissociation'){
        return this.getComplexHtml();
      }
    },
    getOutputHtml: function(){
      if(this.templateType === 'association') {
        return this.getComplexHtml();
      }
      else if(this.templateType === 'dissociation'){
        return this.getMacromoleculesHtml();
      }
    }
  },
  currentTemplateParameters: undefined,
  initialize: function () {
    var self = this;
    self.copyProperties();
    self.template = _.template($("#reaction-template").html(), self.currentTemplateParameters);
  },
  copyProperties: function () {
    this.currentTemplateParameters = jQuery.extend(true, [], this.defaultTemplateParameters);
  },
  render: function () {
    var self = this;
    self.template = _.template($("#reaction-template").html(), self.currentTemplateParameters);
    $(self.el).html(self.template);

    $(self.el).dialog({width:'auto'});

    $('#reaction-template-type-select').die('change').live('change', function (e) {
      var optionSelected = $("option:selected", this);
      var valueSelected = this.value;
      self.currentTemplateParameters.templateType = valueSelected;
      
      self.template = _.template($("#reaction-template").html(), self.currentTemplateParameters);
      $(self.el).html(self.template);

      $(self.el).dialog({width:'auto'});
    });

    $("#template-reaction-enable-complex-name").die("change").live("change", function(e){
      self.currentTemplateParameters.templateReactionEnableComplexName = 
              !self.currentTemplateParameters.templateReactionEnableComplexName;
      self.template = _.template($("#reaction-template").html(), self.currentTemplateParameters);
      $(self.el).html(self.template);

      $(self.el).dialog({width:'auto'});
    });
    
    $("#template-reaction-complex-name").die("change").live("change", function(e){
      self.currentTemplateParameters.templateReactionComplexName = $(this).attr('value');
      self.template = _.template($("#reaction-template").html(), self.currentTemplateParameters);
      $(self.el).html(self.template);

      $(self.el).dialog({width:'auto'});
    });

    $("#template-reaction-add-button").die("click").live("click",function (event) {
      self.currentTemplateParameters.macromoleculeList.push("");
      
      self.template = _.template($("#reaction-template").html(), self.currentTemplateParameters);
      $(self.el).html(self.template);

      $(self.el).dialog({width:'auto'});
    });
    
    $(".template-reaction-textbox").die('change').live('change', function () {
      var index = parseInt($(this).attr('name'));
      var value = $(this).attr('value');
      self.currentTemplateParameters.macromoleculeList[index] = value;
      
      self.template = _.template($("#reaction-template").html(), self.currentTemplateParameters);
      $(self.el).html(self.template);

      $(self.el).dialog({width:'auto'});
    });
    
    $(".template-reaction-delete-button").die("click").live("click",function (event) {
      if(self.currentTemplateParameters.macromoleculeList.length <= 2){
        return;
      }
      
      var index = parseInt($(this).attr('name'));
      self.currentTemplateParameters.macromoleculeList.splice(index, 1);
      
      self.template = _.template($("#reaction-template").html(), self.currentTemplateParameters);
      $(self.el).html(self.template);

      $(self.el).dialog({width:'auto'});
    });

    $("#create-template").die("click").die("click").live("click", function (evt) {
      var param = {
        firstTime: true,
        templateType: self.currentTemplateParameters.templateType,
        processPosition: sbgnElementUtilities.convertToModelPosition({x: cy.width() / 2, y: cy.height() / 2}),
        macromoleculeList: jQuery.extend(true, [], self.currentTemplateParameters.macromoleculeList),
        complexName: self.currentTemplateParameters.templateReactionEnableComplexName?self.currentTemplateParameters.templateReactionComplexName:undefined,
        tilingPaddingVertical: calculateTilingPaddings(parseInt(sbgnStyleRules['tiling-padding-vertical'], 10)),
        tilingPaddingHorizontal: calculateTilingPaddings(parseInt(sbgnStyleRules['tiling-padding-horizontal'], 10))
      };
      
      cy.undoRedo().do("createTemplateReaction", param);
        
      self.copyProperties();
      $(self.el).dialog('close');
    });
    
    $("#cancel-template").die("click").die("click").live("click", function (evt) {
      self.copyProperties();
      $(self.el).dialog('close');
    });
    
    return this;
  }
});