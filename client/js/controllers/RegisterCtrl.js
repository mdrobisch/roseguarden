RoseGuardenApp.controller('RegisterCtrl', function($scope,$q, User, $modal, $log, AuthService) {

    $scope.dataLoading = false;
    $scope.showSuccess = false;
    $scope.showError = false;

    $scope.isAdminRegistration = function () {
        return AuthService.isAdmin();
    };

    $scope.registerAsAdmin = function () {

        $scope.dataLoading = true;
        $scope.sendWelcomeMail = 0;

        var modalInstance = $modal.open({
          templateUrl: 'partials/modals/SendWelcomeMail.html',
          controller: 'SendWelcomeMailCtrl',
          windowClass: 'center-modal',
          resolve: {
            name: function () {
                return $scope.newuser.firstName + ' ' + $scope.newuser.lastName; }
          }
        });


        modalInstance.result.then(function (result) {
            $scope.sendWelcomeMail = result;
            $log.info('SendWelcomeMail set to : ' + $scope.sendWelcomeMail);

            deferred = $q.defer();

            console.log($scope.sendWelcomeMail)

            var newuser = {password:btoa($scope.newuser.password), firstName:$scope.newuser.firstName, lastName: $scope.newuser.lastName, phone: $scope.newuser.phone, association : $scope.newuser.association, email: $scope.newuser.email, sendWelcomeMail: $scope.sendWelcomeMail};

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
        }, function () {
          $log.info('Modal dismissed at: ' + new Date());
        })

    }

    $scope.registerAsNewUser = function () {
        deferred = $q.defer();

        console.log($scope.sendWelcomeMail)

        var newuser = {password:btoa($scope.newuser.password), firstName:$scope.newuser.firstName, lastName: $scope.newuser.lastName, phone: $scope.newuser.phone, association : $scope.newuser.association, email: $scope.newuser.email, sendWelcomeMail: 0};

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


    $scope.register = function() {
        if(AuthService.isAdmin() == true)
        {
            console.log("As admin");
            return $scope.registerAsAdmin();
        }
        else
        {
            console.log("As new User");
            return $scope.registerAsNewUser();
        }
    };
})