RoseGuardenApp.factory('User', function(Restangular) {
    var User;
    User = {
        get: function(id,bypassErrorInterceptor) {
            return Restangular
                .one('user',id)
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .get(id);
        },
        update: function(id,data) {
            return Restangular
                .one('user',id)
                .withHttpConfig({bypassErrorInterceptor: true})
                .customPOST(data);
        },
        register: function(data) {
            return Restangular
                .one('register')
                .withHttpConfig({bypassErrorInterceptor: true})
                .customPOST(data);
        }

    };
    return User;
})