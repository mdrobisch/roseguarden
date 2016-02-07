RoseGuardenApp.factory('User', function(Restangular) {
    var User;
    User = {
        get: function(id,bypassErrorInterceptor) {
            return Restangular
                .one('user',id)
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .get(id);
        },
        getList: function (bypassErrorInterceptor) {
            return Restangular
                .all('users')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .getList();
        },
        getAdminsList: function (bypassErrorInterceptor) {
            return Restangular
                .all('admins')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .getList();
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
        },
        delete: function(id) {
            return Restangular
                .one('user',id)
                .withHttpConfig({bypassErrorInterceptor: true})
                .remove();
        }

    };
    return User;
})