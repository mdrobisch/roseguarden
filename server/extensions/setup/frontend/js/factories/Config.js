RoseGuardenApp.factory('Config', function(Restangular) {
    var Config;
    Config = {
        get: function(data, bypassErrorInterceptor) {
            return Restangular
                .one('config')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .customGET(data);
        },
        update: function(data, bypassErrorInterceptor) {
            return Restangular
                .one('config')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .customPOST(data);
        }
    };
    return Config;
});
