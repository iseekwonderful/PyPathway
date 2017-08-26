var sbgnElementUtilities = {
    //the list of the element classes handled by the tool
    handledElements: {'unspecified entity': true, 'simple chemical': true, 'macromolecule': true,
        'nucleic acid feature': true, 'perturbing agent': true, 'source and sink': true,
        'complex': true, 'process': true, 'omitted process': true, 'uncertain process': true,
        'association': true, 'dissociation': true, 'phenotype': true,
        'tag': true, 'consumption': true, 'production': true, 'modulation': true,
        'stimulation': true, 'catalysis': true, 'inhibition': true, 'necessary stimulation': true,
        'logic arc': true, 'equivalence arc': true, 'and operator': true,
        'or operator': true, 'not operator': true, 'and': true, 'or': true, 'not': true,
        'nucleic acid feature multimer': true, 'macromolecule multimer': true,
        'simple chemical multimer': true, 'complex multimer': true, 'compartment': true},
    //this method returns the nodes non of whose ancestors is not in given nodes
    getTopMostNodes: function (nodes) {
        var nodesMap = {};
        for (var i = 0; i < nodes.length; i++) {
            nodesMap[nodes[i].id()] = true;
        }
        var roots = nodes.filter(function (i, ele) {
            var parent = ele.parent()[0];
            while(parent != null){
              if(nodesMap[parent.id()]){
                return false;
              }
              parent = parent.parent()[0];
            }
            return true;
        });

        return roots;
    },
    //This method checks if all of the given nodes have the same parent assuming that the size 
    //of  nodes is not 0
    allHaveTheSameParent: function (nodes) {
        if (nodes.length == 0) {
            return true;
        }
        var parent = nodes[0].data("parent");
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            if (node.data("parent") != parent) {
                return false;
            }
        }
        return true;
    },
    //This method propogates given replacement to the children of the given node recursively
    propogateReplacementToChildren: function (node, dx, dy) {
        var children = node.children();
        for(var i = 0; i < children.length; i++){
            var child = children[i];
            child.position({
               x: child.position('x') + dx,
               y: child.position('y') + dy
            });
            
            this.propogateReplacementToChildren(child, dx, dy);
        }
    },
    moveNodes: function(positionDiff, nodes, notCalcTopMostNodes) {
      var topMostNodes = notCalcTopMostNodes ? nodes : sbgnElementUtilities.getTopMostNodes(nodes);
      for (var i = 0; i < topMostNodes.length; i++) {
        var node = topMostNodes[i];
        var oldX = node.position("x");
        var oldY = node.position("y");
        node.position({
          x: oldX + positionDiff.x,
          y: oldY + positionDiff.y
        });
        var children = node.children();
        this.moveNodes(positionDiff, children, true);
      }
    },
    convertToModelPosition: function (renderedPosition) {
      var pan = cy.pan();
      var zoom = cy.zoom();

      var x = (renderedPosition.x - pan.x) / zoom;
      var y = (renderedPosition.y - pan.y) / zoom;

      return {
        x: x,
        y: y
      };
    }
};