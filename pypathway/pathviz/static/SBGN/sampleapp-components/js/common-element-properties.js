var getCommonSBGNClass = function(elements){
  if(elements.length < 1){
    return "";
  }
  
  var SBGNClassOfFirstElement = elements[0].data('sbgnclass');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].data('sbgnclass') != SBGNClassOfFirstElement){
      return "";
    }
  }
  
  return SBGNClassOfFirstElement;
};

var allAreNode = function(elements){
  for(var i = 0; i <elements.length; i++){
    var ele = elements[i];
    if(!ele.isNode()){
      return false;
    }
  }
  
  return true;
};

var allAreEdge = function(elements){
  for(var i = 0; i <elements.length; i++){
    var ele = elements[i];
    if(!ele.isEdge()){
      return false;
    }
  }
  
  return true;
};

var allCanHaveStateVariable = function(elements){
  for(var i = 0; i <elements.length; i++){
    var ele = elements[i];
    if(!canHaveStateVariable(ele.data('sbgnclass'))){
      return false;
    }
  }
  
  return true;
};

var allCanHaveUnitOfInformation = function(elements){
  for(var i = 0; i <elements.length; i++){
    var ele = elements[i];
    if(!canHaveUnitOfInformation(ele.data('sbgnclass'))){
      return false;
    }
  }
  
  return true;
};

var getCommonStateAndInfos = function(elements){
  if(elements.length == 0){
    return [];
  }
  
  var firstStateOrInfo = elements[0]._private.data.sbgnstatesandinfos;
  for(var i = 1; i <elements.length; i++){
    if(!_.isEqual(elements[i]._private.data.sbgnstatesandinfos, firstStateOrInfo)){
      return null;
    }
  }
  
  return firstStateOrInfo;
};

var allCanBeCloned = function(elements){
  for(var i = 0; i <elements.length; i++){
    var ele = elements[i];
    if(!canBeCloned(ele.data('sbgnclass'))){
      return false;
    }
  }
  
  return true;
};

var allCanBeMultimer = function(elements){
  for(var i = 0; i <elements.length; i++){
    var ele = elements[i];
    if(!canBeMultimer(ele.data('sbgnclass'))){
      return false;
    }
  }
  
  return true;
};

var getCommonIsCloned = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var firstElementIsCloned = elements[0].data('sbgnclonemarker');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].data('sbgnclonemarker') != firstElementIsCloned){
      return null;
    }
  }
  
  return firstElementIsCloned;
};

var getCommonIsMultimer = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var firstElementIsMultimer = elements[0].data('sbgnclass').endsWith(' multimer');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].data('sbgnclass').endsWith(' multimer') != firstElementIsMultimer){
      return null;
    }
  }
  
  return firstElementIsMultimer;
};

var getCommonLabel = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var labelOfFirstElement = elements[0].data('sbgnlabel');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].data('sbgnlabel') != labelOfFirstElement){
      return null;
    }
  }
  
  return labelOfFirstElement;
};

var getCommonBorderColor = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var borderColorOfFirstElement = elements[0].data('borderColor');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].data('borderColor') != borderColorOfFirstElement){
      return null;
    }
  }
  
  return borderColorOfFirstElement;
};

var getCommonFillColor = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var fillColorOfFirstElement = elements[0].css('background-color');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].css('background-color') != fillColorOfFirstElement){
      return null;
    }
  }
  
  return fillColorOfFirstElement;
};

var getCommonBorderWidth = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var borderWidthOfFirstElement = elements[0].css('border-width');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].css('border-width') != borderWidthOfFirstElement){
      return null;
    }
  }
  
  return borderWidthOfFirstElement;
};

var getCommonBackgroundOpacity = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var backgroundOpacityOfFirstElement = elements[0].data('backgroundOpacity');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].data('backgroundOpacity') != backgroundOpacityOfFirstElement){
      return null;
    }
  }
  
  return backgroundOpacityOfFirstElement;
};

var getCommonLineColor = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var lineColorOfFirstElement = elements[0].data('lineColor');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].data('lineColor') != lineColorOfFirstElement){
      return null;
    }
  }
  
  return lineColorOfFirstElement;
};

var getCommonLineWidth = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var lineWidthOfFirstElement = elements[0].css('width');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].css('width') != lineWidthOfFirstElement){
      return null;
    }
  }
  
  return lineWidthOfFirstElement;
};

var getCommonSBGNCardinality = function(elements){
  if(elements.length == 0){
    return undefined;
  }
  
  var cardinalityOfFirstElement = elements[0].data('sbgncardinality');
  for(var i = 1; i < elements.length; i++){
    if(elements[i].data('sbgncardinality') != cardinalityOfFirstElement){
      return undefined;
    }
  }
  
  return cardinalityOfFirstElement;
};

var canHaveSBGNCardinality = function(ele) {
  return ele.data('sbgnclass') == 'consumption' || ele.data('sbgnclass') == 'production';
};

var allCanHaveSBGNCardinality = function(elements){
  for(var i = 0; i < elements.length; i++){
    if(!canHaveSBGNCardinality(elements[i])){
      return false;
    }
  }
  
  return true;
};

var getCommonNodeWidth = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var widthOfFirstElement = elements[0].width();
  for(var i = 1; i < elements.length; i++){
    if(elements[i].width() != widthOfFirstElement){
      return null;
    }
  }
  
  return widthOfFirstElement;
};

var getCommonNodeHeight = function(elements){
  if(elements.length == 0){
    return null;
  }
  
  var heightOfFirstElement = elements[0].height();
  for(var i = 1; i < elements.length; i++){
    if(elements[i].width() != heightOfFirstElement){
      return null;
    }
  }
  
  return heightOfFirstElement;
};

var stringAfterValueCheck = function (value) {
  return value ? value : '';
};

var canHaveUnitOfInformation = function(sbgnclass) {
   if (sbgnclass == 'simple chemical'
          || sbgnclass == 'macromolecule' || sbgnclass == 'nucleic acid feature'
          || sbgnclass == 'complex' || sbgnclass == 'simple chemical multimer'
          || sbgnclass == 'macromolecule multimer' || sbgnclass == 'nucleic acid feature multimer'
          || sbgnclass == 'complex multimer') {
    return true;
  }
  return false;
};

var canHaveStateVariable = function(sbgnclass) {
   if (sbgnclass == 'macromolecule' || sbgnclass == 'nucleic acid feature'
          || sbgnclass == 'complex' 
          || sbgnclass == 'macromolecule multimer' || sbgnclass == 'nucleic acid feature multimer'
          || sbgnclass == 'complex multimer') {
    return true;
  }
  return false;
};

var mustBeSquare = function(sbgnclass) {
  return (sbgnclass.indexOf('process') != -1 || sbgnclass == 'source and sink'
          || sbgnclass == 'and' || sbgnclass == 'or' || sbgnclass == 'not'
          || sbgnclass == 'association' || sbgnclass == 'dissociation');
};

var someMustNotBeSquare = function(nodes) {
  for (var i = 0; i < nodes.length; i++) {
    var node = nodes[i];
    if ( !mustBeSquare(node.data('sbgnclass')) ) {
      return true;
    }
  }
  
  return false;
};

var isCollapsedOrParent = function(node) {
  return (node.data('collapsedChildren') != null || ( node.children() && node.children().length > 0 ));
};

var includesNotCollapsedNorParentElement = function(nodes) {
  for (var i = 0; i < nodes.length; i++) {
    var node = nodes[i];
    if ( !isCollapsedOrParent(node) ) {
      return true;
    }
  }
  
  return false;
};

//checks if a node with the given sbgnclass can be cloned
var canBeCloned = function (sbgnclass) {
  sbgnclass = sbgnclass.replace(" multimer", "");
  var list = {
    'unspecified entity': true,
    'macromolecule': true,
    'complex': true,
    'nucleic acid feature': true,
    'simple chemical': true,
    'perturbing agent': true
  };

  return list[sbgnclass] ? true : false;
};

//checks if a node with the given sbgnclass can become a multimer
var canBeMultimer = function (sbgnclass) {
  sbgnclass = sbgnclass.replace(" multimer", "");
  var list = {
    'macromolecule': true,
    'complex': true,
    'nucleic acid feature': true,
    'simple chemical': true
  };

  return list[sbgnclass] ? true : false;
};

var isEPNClass = function (sbgnclass) {
  return (sbgnclass == 'unspecified entity'
          || sbgnclass == 'simple chemical'
          || sbgnclass == 'macromolecule'
          || sbgnclass == 'nucleic acid feature'
          || sbgnclass == 'complex');
};

var isPNClass = function (sbgnclass) {
  return (sbgnclass == 'process'
          || sbgnclass == 'omitted process'
          || sbgnclass == 'uncertain process'
          || sbgnclass == 'association'
          || sbgnclass == 'dissociation');
};

var isLogicalOperator = function (sbgnclass) {
  return (sbgnclass == 'and' || sbgnclass == 'or' || sbgnclass == 'not');
};

var convenientToEquivalence = function (sbgnclass) {
  return (sbgnclass == 'tag' || sbgnclass == 'terminal');
};