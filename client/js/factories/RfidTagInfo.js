/**
 * Created by drobisch on 20.10.15.
 */
RoseGuardenApp.factory('RfidTagInfo', function(Restangular) {
    var RfidTagInfo;
    RfidTagInfo = {
        get: function() {
            return Restangular
                .one('taginfo')
                .withHttpConfig({bypassErrorInterceptor: true})
                .get();
        }
    };
    return RfidTagInfo;
})