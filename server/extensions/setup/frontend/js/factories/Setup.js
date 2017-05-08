RoseGuardenApp.factory('Setup', function(Restangular) {
    var Setup;
    Setup = {
        getStatus: function(data, bypassErrorInterceptor) {
            return Restangular
                .one('setup/status')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .customGET(data);
        },
        start: function(data, bypassErrorInterceptor) {
            return Restangular
                .one('setup/start')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .customPOST(data);
        },
        lock: function(data,bypassErrorInterceptor) {
            return Restangular
                .one('setup/lock')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .customPOST(data);
        }
    };
    return Setup;
});
