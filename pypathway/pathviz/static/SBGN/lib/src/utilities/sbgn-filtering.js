var sbgnFiltering = {
    processTypes : ['process', 'omitted process', 'uncertain process', 
        'association', 'dissociation', 'phenotype'],

    deleteSelected: function(){
        var allNodes = cy.nodes();
        var selectedNodes = cy.nodes(":selected");
        cy.elements().unselect();
        var nodesToShow = this.expandRemainingNodes(selectedNodes, allNodes);
        var nodesNotToShow = allNodes.not(nodesToShow);
        var connectedEdges = nodesNotToShow.connectedEdges();
        var removedEles = connectedEdges.remove();
        removedEles = removedEles.union(nodesNotToShow.remove());
        return removedEles;
    },

    getProcessesOfSelected: function(){
        var selectedEles = cy.elements(":selected");
        selectedEles = this.expandNodes(selectedEles);
        return selectedEles;
    },
    
    getNeighboursOfSelected: function(){
        var selectedEles = cy.elements(":selected");
        selectedEles = selectedEles.add(selectedEles.parents("node[sbgnclass='complex']"));
        selectedEles = selectedEles.add(selectedEles.descendants());
        var neighborhoodEles = selectedEles.neighborhood();
        var elesToHighlight = selectedEles.add(neighborhoodEles);
        elesToHighlight = elesToHighlight.add(elesToHighlight.descendants());
        return elesToHighlight;
    },

    expandNodes: function(nodesToShow){
        var self = this;
        //add children
        nodesToShow = nodesToShow.add(nodesToShow.nodes().descendants());
        //add parents
        nodesToShow = nodesToShow.add(nodesToShow.parents());
        //add complex children
        nodesToShow = nodesToShow.add(nodesToShow.nodes("node[sbgnclass='complex']").descendants());

        // var processes = nodesToShow.nodes("node[sbgnclass='process']");
        // var nonProcesses = nodesToShow.nodes("node[sbgnclass!='process']");
        // var neighborProcesses = nonProcesses.neighborhood("node[sbgnclass='process']");

        var processes = nodesToShow.filter(function(){
            return $.inArray(this._private.data.sbgnclass, self.processTypes) >= 0;
        });
        var nonProcesses = nodesToShow.filter(function(){
            return $.inArray(this._private.data.sbgnclass, self.processTypes) === -1;
        });
        var neighborProcesses = nonProcesses.neighborhood().filter(function(){
            return $.inArray(this._private.data.sbgnclass, self.processTypes) >= 0;
        });

        nodesToShow = nodesToShow.add(processes.neighborhood());
        nodesToShow = nodesToShow.add(neighborProcesses);
        nodesToShow = nodesToShow.add(neighborProcesses.neighborhood());

        //add parents
        nodesToShow = nodesToShow.add(nodesToShow.nodes().parents());
        //add children
        nodesToShow = nodesToShow.add(nodesToShow.nodes("node[sbgnclass='complex']").descendants());

        return nodesToShow;
    },

    expandRemainingNodes: function(nodesToFilter, allNodes){
        nodesToFilter = this.expandNodes(nodesToFilter);
        var nodesToShow = allNodes.not(nodesToFilter);
        nodesToShow = this.expandNodes(nodesToShow);
        return nodesToShow;
    },
    
    noneIsNotHighlighted: function(){
        var notHighlightedNodes = cy.nodes(":visible").nodes(".nothighlighted");
        var notHighlightedEdges = cy.edges(":visible").edges(".nothighlighted");
        
        return notHighlightedNodes.length + notHighlightedEdges.length === 0;
    }
};