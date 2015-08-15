RoseGuardenApp.factory('PasswordRequest', function(Restangular) {
    var PasswordRequest;
    PasswordRequest = {
        create: function(data, bypassErrorInterceptor) {
            return Restangular
                .one('request')
                .one('password')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .customPOST(data);
        }
    };
    return PasswordRequest;
})
