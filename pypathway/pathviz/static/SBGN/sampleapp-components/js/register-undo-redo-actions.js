var registerUndoRedoActions = function () {
  // create undo-redo instance
  var ur = cy.undoRedo({
    keyboardShortcuts: {
      ctrl_z: false, // undo
      ctrl_y: false, // redo
      ctrl_shift_z: false // redo
    }
  });

  // register general actions
  ur.action("changeBendPoints", generalActionFunctions.changeBendPoints, generalActionFunctions.changeBendPoints);
  
  // register add remove actions
  ur.action("removeEles", addRemoveActionFunctions.removeEles, addRemoveActionFunctions.restoreEles);
  ur.action("deleteSelected", addRemoveActionFunctions.deleteSelected, addRemoveActionFunctions.restoreSelected);
};