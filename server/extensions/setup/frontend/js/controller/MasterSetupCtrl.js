RoseGuardenApp.controller('MasterSetupCtrl', function($scope, $q, Config, $location) {

    var i=0;
    i++;
    $scope.isLoading = true;
    
    this.loadConfig = function(credentials) {
        var me = this;
        deferred = $q.defer();
        Config.create(credentials, true).then(function(config) {
            currentConfig = JSON.parse(config);
            console.log("got it");
            return deferred.resolve(config);
        }, function(response) {
            console.log("rejected");
            return deferred.reject(response);
        });
        return deferred.promise
    };


    $scope.finishSetup = function () {
        console.log("Test");
    };

});