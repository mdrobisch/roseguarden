RoseGuardenApp.factory('Statistic', function(Restangular) {
    var Statistic;
    Statistic = {
        getList: function (bypassErrorInterceptor) {
            return Restangular
                .all('statistics')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .getList();
        },
        getEntryList: function(id) {
            return Restangular
                .one('statistic',id)
                .withHttpConfig({bypassErrorInterceptor: true})
                .getList();
        }
    };
    return Statistic;
})