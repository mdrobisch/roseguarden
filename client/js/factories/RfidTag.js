/**
 * Created by drobisch on 20.10.15.
 */
RoseGuardenApp.factory('RfidTag', function(Restangular) {
    var RfidTagInfo;
    RfidTagInfo = {
        get: function() {
            return Restangular
                .one('taginfo')
                .one('info')
                .withHttpConfig({bypassErrorInterceptor: true})
                .get();
        }
    };
    return RfidTagInfo;
})