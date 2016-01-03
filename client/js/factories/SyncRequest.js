/**
 * Created by drobisch on 03.01.16.
 */
RoseGuardenApp.factory('SyncRequest', function(Restangular) {
    var SyncRequest;
    SyncRequest = {
        create: function(bypassErrorInterceptor) {
            return Restangular
                .one('request')
                .one('sync')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .post();
        }
    };
    return SyncRequest;
})