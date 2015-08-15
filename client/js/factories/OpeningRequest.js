RoseGuardenApp.factory('OpeningRequest', function(Restangular) {
    var OpeningRequest;
    OpeningRequest = {
        create: function(data,destination) {
            return Restangular.withConfig(function(RestangularConfigurer) {
                RestangularConfigurer.setBaseUrl(destination + ':5000')})
                .one('request')
                .one('opening')
                .customPOST(data);
        }
    };
    return OpeningRequest;
})