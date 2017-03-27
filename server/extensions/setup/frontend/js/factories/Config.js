RoseGuardenApp.factory('Config', function(Restangular) {
    var Config;
    Config = {
        create: function(data, bypassErrorInterceptor) {
            return Restangular
                .one('config')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .customGET(data);
        }
    };
    return Config;
});
