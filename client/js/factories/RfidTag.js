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
        },
        postAssign: function(data) {
            return Restangular
                .one('tag')
                .one('assign')
                .withHttpConfig({bypassErrorInterceptor: true})
                .customPOST(data);
        },
        postWithdraw: function(data) {
            return Restangular
                .one('tag')
                .one('withdraw')
                .withHttpConfig({bypassErrorInterceptor: true})
                .customPOST(data);
        }
    };
    return RfidTagInfo;
})