RoseGuardenApp.controller('RegisterCtrl', function($scope,$q,User) {

    $scope.dataLoading = false;
    $scope.showSuccess = false;
    $scope.showError = false;

    $scope.register = function() {
        $scope.dataLoading = true;
        deferred = $q.defer();
        var newuser = {password:btoa($scope.newuser.password), firstName:$scope.newuser.firstName, lastName: $scope.newuser.lastName, phone: $scope.newuser.phone, email: $scope.newuser.email};

        User.register(newuser).then(function() {
            $scope.dataLoading = false;
            $scope.showError = false;
            $scope.showSuccess = true;
            return deferred.resolve();
        }, function(response) {
            $scope.error = 'Register new user failed' + ' (' + response.data.error + ' )'
            $scope.dataLoading = false;
            $scope.showSuccess = false;
            $scope.showError = true;
            return deferred.reject(response);
        });
        return deferred.promise

    };
})