/**
 * Created by drobisch on 20.10.15.
 */
RoseGuardenApp.factory('RfidTag', function(Restangular) {
    var RfidTagInfo;
    RfidTagInfo = {
        getInfo: function() {
            return Restangular
                .one('tag')
                .one('info')
                .withHttpConfig({bypassErrorInterceptor: true})
                .get();
        }
    };
    return RfidTagInfo;
})