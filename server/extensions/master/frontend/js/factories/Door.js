RoseGuardenApp.factory('Door', function(Restangular) {
    var Door;
    Door = {
        getList: function() {
            return Restangular
                .one('doors')
                .withHttpConfig({bypassErrorInterceptor: true})
                .getList();
        },
        register: function(data) {
            return Restangular
                .one('door')
                .withHttpConfig({bypassErrorInterceptor: true})
                .customPOST(data);
        },
        synchronize: function(data) {
            return Restangular
                .one('door', id)
                .one('sync')
                .withHttpConfig({bypassErrorInterceptor: true})
                .customPOST(data);
        },
        delete: function(id) {
            return Restangular
                .one('door',id)
                .withHttpConfig({bypassErrorInterceptor: true})
                .remove();
        }

    };
    return Door;
})