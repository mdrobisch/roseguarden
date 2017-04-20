RoseGuardenApp.factory('Setup', function(Restangular) {
    var Setup;
    Setup = {
        getStatus: function(data, bypassErrorInterceptor) {
            return Restangular
                .one('setup/status')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .customGET(data);
        },
        lock: function(id,data) {
            return Restangular
                .one('/setup/lock', id)
                .withHttpConfig({bypassErrorInterceptor: true})
                .customPOST(data);
        }
    };
    return Setup;
});
