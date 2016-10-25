var addRemoveActionFunctions = {
  removeEles: function (elesToBeRemoved) {
    return addRemoveUtilities.removeEles(elesToBeRemoved);
  },
  restoreEles: function (eles) {
    return addRemoveUtilities.restoreEles(eles);
  },
  restoreSelected: function (eles) {
    var param = {};
    param.eles = addRemoveUtilities.restoreEles(eles);
    param.firstTime = false;
    return param;
  },
  deleteSelected: function (param) {
    if (param.firstTime) {
      return sbgnFiltering.deleteSelected();
    }
    return addRemoveUtilities.removeElesSimply(param.eles);
  },
};