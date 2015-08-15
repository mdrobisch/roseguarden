RoseGuardenApp.factory('Door', function(Restangular) {
    var Door;
    Door = {
        get: function() {
            return Restangular
                .one('doors')
                .withHttpConfig({bypassErrorInterceptor: true})
                .getList();
        },
        create: function(data) {
            return Restangular
                .one('doors')
                .customPOST(data);
        }
    };
    return Door;
})