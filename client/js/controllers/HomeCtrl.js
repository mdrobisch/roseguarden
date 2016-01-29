RoseGuardenApp.controller('HomeCtrl', function($q, $scope, Door, AuthService, $log, OpeningRequest, User) {

    $scope.message = '';
    $scope.isLoading = true;
    $scope.showError = false;

    $scope.doors = [
        //{name: 'outer door', licenseMask: 0x01, address:'192.168.1.168'},
        //{name: 'inner door', licenseMask: 0x00, address:'192.168.6.168'}
    ];

    $scope.isAllowed = function(door) {
        if((door.keyMask & $scope.user.keyMask)  != 0)
            return false;
        else
            return true;
    }

    $scope.requestOpening = function (door) {
        $scope.message = 'Request send to door (' + door.address +  ') ... ';
        var me = this;
        deferred = $q.defer();
        OpeningRequest.create(null, door.address).then(function(response) {
            console.log(response)
            $scope.message =  $scope.message + response;
            return deferred.resolve();
        }, function(response) {
            console.log(response)
            $scope.message =  $scope.message + response;
            return deferred.reject(response);
        });
        return deferred.promise
    }


    // starts here
    AuthService.loadCurrentUser().then(function(user) {

        $scope.user = user;
        //console.log(user);


        Door.getList().then(function(doors) {
            $scope.doors = doors;
            $scope.isLoading = false;
        }, function(response) {
            $scope.showError = true;
            $scope.isLoading = false;
        });
    }, function(response) {

    });




})