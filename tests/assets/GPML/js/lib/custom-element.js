function initPvjs() {

  var Pvjs = require('./main.js');

  /**
   * Enable the wikipathways-pvjs custom element
   *
   * @return
   */
  function registerWikiPathwaysPvjsElement(Pvjs) {
    'use strict';

    var DivPrototype = Object.create(window.HTMLDivElement.prototype);

    DivPrototype.attributeChangedCallback = function(
        attrName, oldValue, newValue) {
      if (attrName === 'alt') {
        this.textContent = newValue;
      }
    };

    var WikiPathwaysPvjsPrototype = Object.create(DivPrototype);

    WikiPathwaysPvjsPrototype.createdCallback = function() {
      var vm = this;
      var args = {};

      var alt = args.alt = vm.getAttribute('alt');
      if (!!alt) {
        vm.attributeChangedCallback('alt', null, alt);
      }

      var displayErrors = args.displayErrors =
          Boolean(vm.getAttribute('display-errors'));
      vm.attributeChangedCallback('display-errors', null, displayErrors);

      var displayWarnings = args.displayWarnings =
          Boolean(vm.getAttribute('display-warnings'));
      vm.attributeChangedCallback('display-warnings', null, displayWarnings);

      var displaySuccess = args.displaySuccess =
          Boolean(vm.getAttribute('display-success'));
      vm.attributeChangedCallback('display-success', null, displaySuccess);

      var fitToContainer = args.fitToContainer =
          Boolean(vm.getAttribute('fit-to-container'));
      vm.attributeChangedCallback('fit-to-container', null, fitToContainer);

      var highlights = vm.getAttribute('highlights');
      if (!!highlights) {
        highlights = args.highlights = JSON.parse(decodeURIComponent(highlights));
        vm.attributeChangedCallback('highlights', null, highlights);
      }

      var hashEditorStateComponents = window.location.hash.match('editor\/(.*)$');
      var hashEditorState;
      if (!!hashEditorStateComponents && !!hashEditorStateComponents.length) {
        hashEditorState = hashEditorStateComponents[1];
      }
      var editor = args.editor = hashEditorState ||
          vm.getAttribute('editor');
      if (!!editor) {
        vm.attributeChangedCallback('editor', null, editor);
      }

      var resource = args.resource = vm.getAttribute('resource');
      if (!!resource) {
        vm.attributeChangedCallback('resource', null, resource);
      }

      var version = args.version = parseFloat(vm.getAttribute('version'));
      if (!!version) {
        vm.attributeChangedCallback('version', null, version);
      }

      /* TODO should this be enabled? It doesn't seem needed for the web-component.
      var manualRender = args.manualRender =
          Boolean(vm.getAttribute('manual-render'));
      if (!!manualRender) {
        vm.attributeChangedCallback('manual-render', null, manualRender);
      }
      //*/

      var src = vm.getAttribute('src');
      if (!!src) {
        vm.attributeChangedCallback('src', null, src);
      }
      args.sourceData = [
        {
          uri: src,
          // TODO we should be able to use the content type
          // header from the server response instead of relying
          // on this.
          // Think analogous to image/png, image/gif, etc. for the img tag.
          fileType:'gpml' // generally will correspond to filename extension
        }
      ];

      //vm.innerHTML = '';

      var pvjs = new Pvjs(vm, args);
    };

    // Public: WikiPathwaysPvjsPrototype constructor.
    //
    //   # => <wikipathways-pvjs></wikipathways-pvjs>
    //
    window.WikiPathwaysPvjs = document.registerElement(
        'wikipathways-pvjs', {
        prototype: WikiPathwaysPvjsPrototype
    });
  }

  if (!!window.Kaavio) {
    registerWikiPathwaysPvjsElement(Pvjs);
  } else {
    window.addEventListener('kaavioready', function kaavioReadyHandler(e) {
      window.removeEventListener('kaavioready', kaavioReadyHandler, false);
      registerWikiPathwaysPvjsElement(Pvjs);
    }, false);
  }
}

if (document.readyState === 'complete') {
  initPvjs();
} else {
  window.addEventListener('load', function listener(event) {
    window.removeEventListener('load', listener, false);
    initPvjs();
  }, false);
}
