/**
 * Created by drobisch on 26.07.15.
 */
RoseGuardenApp.factory('Log', function(Restangular) {
    var Log;
    Log = {
        getAdminLog: function (bypassErrorInterceptor) {
            return Restangular
                .all('actions/admin')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .getList();
        },
        getDebugLog: function (bypassErrorInterceptor) {
            return Restangular
                .all('actions/debug')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .getList();
        },
        getUserLog: function (bypassErrorInterceptor) {
            return Restangular
                .all('actions/user')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .getList();
        }


    };
    return Log;
})