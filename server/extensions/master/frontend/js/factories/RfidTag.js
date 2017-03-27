/**
 * Created by drobisch on 20.10.15.
 */
RoseGuardenApp.factory('RfidTag', function(Restangular) {
    var RfidTagInfo;
    RfidTagInfo = {
        getInfo: function() {
            return Restangular
                .one('auth')
                .one('info')
                .withHttpConfig({bypassErrorInterceptor: true})
                .get();
        },
        postAssign: function(data) {
            return Restangular
                .one('auth')
                .one('assign')
                .withHttpConfig({bypassErrorInterceptor: true})
                .customPOST(data);
        },
        postWithdraw: function(data) {
            return Restangular
                .one('auth')
                .one('withdraw')
                .withHttpConfig({bypassErrorInterceptor: true})
                .customPOST(data);
        }
    };
    return RfidTagInfo;
})