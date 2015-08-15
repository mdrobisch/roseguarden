RoseGuardenApp.controller('LostPasswordCtrl', function($scope,PasswordRequest) {

    $scope.submit = function() {
        $scope.message = 'send new password';
        $scope.dataLoading = true;

        PasswordRequest.create($scope.credentials,true).then(function() {
            $scope.error = null;
            $scope.succeed = 'New password send to your eMail-address';
            $scope.dataLoading = false;
        }, function(response) {

            $scope.succeed = null
            switch (response.status) {
                case 0:
                    $scope.error = 'Server not available (' + response.status + ').';
                    break;
                case 401:
                    $scope.error = 'Failed to send password please check eMail-address (' + response.status + ').';
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