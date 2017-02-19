/**
 * Created by drobisch on 16.10.15.
 */

RoseGuardenApp.filter('moment', function () {
    return function(dateString, format) {
        return moment.utc(new Date(dateString)).format(format);
    };
});