/**
 * Created by drobisch on 01.08.15.
 */
RoseGuardenApp.directive('stRatio', [function () {

    return {
      link:function(scope, element, attr){
        var ratio=+(attr.stRatio);

        element.css('width',ratio+'%');

      }
    };
}]);