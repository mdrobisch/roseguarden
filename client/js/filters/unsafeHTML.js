/**
 * Created by drobisch on 20.10.15.
 */

RoseGuardenApp.filter('unsafeHTML', function($sce) {
    return function(val) {
        return $sce.trustAsHtml(val);
    };
});