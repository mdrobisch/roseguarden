RoseGuardenApp.service('ConfigService', ConfigService = function($q, Config) {

    var currentConfig = null;
    console.log("Config service loaded");

    this.loadConfig = function(credentials) {
        var me = this;
        deferred = $q.defer();
        Config.create(credentials, true).then(function(config) {
            currentConfig = JSON.parse(config);

            return deferred.resolve(config);
        }, function(response) {
            return deferred.reject(response);
        });
        return deferred.promise
    };

    currentConfig = this.loadConfig(null);

    this.getConfig = function () {
      return currentConfig;

    };


    return this;
});

