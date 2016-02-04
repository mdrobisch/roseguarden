RoseGuardenApp.factory('InvalidateAuthCardRequest', function(Restangular) {
    var LostAuthCardRequest;
    LostAuthCardRequest = {
        create: function(id, bypassErrorInterceptor) {
            return Restangular
                .one('request')
                .one('invalidateAuthCard',id)
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .post();
        }
    };
    return LostAuthCardRequest;
})
