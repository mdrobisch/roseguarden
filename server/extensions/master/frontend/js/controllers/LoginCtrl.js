RoseGuardenApp.controller('LoginCtrl', function($scope, $location, Session, AuthService) {

    $scope.login = function() {
        $scope.dataLoading = true;
        AuthService.login($scope.credentials).then(function(user) {
            console.log("user: " + user.email);
            $location.path('/')
        }, function(response) {

            switch (response.status) {
                case 0:
                    $scope.error = 'Server not available (' + response.status + ').';
                    break;
                case 401:
                    $scope.error = 'Failed to login, please retry (' + response.status + ').';
                    break;
                default:
                    throw new Error('No handler for status code (' + response.status + ').');
            }

            //$scope.error = btoa($scope.credentials.email + ":" +  $scope.credentials.password);
            $scope.failedLoginAttempt = true;
            $scope.dataLoading = false;
        });

    };
})