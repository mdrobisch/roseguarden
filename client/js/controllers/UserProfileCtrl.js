RoseGuardenApp.controller('UserProfileCtrl', function ($scope, $location, $q, AuthService, User, $modal, $log, InvalidateAuthCardRequest) {

    $scope.updateProfile = function() {
        $scope.profileUpdatePending = true;
        var me = this;
        deferred = $q.defer();
        User.update(AuthService.getCurrentUserID(), $scope.user).then(function() {
            $scope.profileUpdatePending = false;
            $scope.success = 'Profile successfully changed.'
            $scope.showError = false;
            $scope.showSuccess = true;
            return deferred.resolve();
        }, function(response) {
            $scope.error = 'Updating profile failed.'
            $scope.profileUpdatePending = false;
            $scope.showError = true;
            $scope.showSuccess = false;
            return deferred.reject(response);
        });
        return deferred.promise
    };

    $scope.lostAuthCard = function() {

        var modalInstance = $modal.open({
          templateUrl: 'partials/modals/LostAuthCard.html',
          controller: 'InvalidateRFIDCtrl',
          windowClass: 'center-modal',
          resolve: {
            name: function () {
                return 0; }
          }
        });

        modalInstance.result.then(function (selected) {

            InvalidateAuthCardRequest.create(AuthService.getCurrentUserID()).then(function() {
                $scope.profileUpdatePending = false;
                $scope.success = 'Lost card successfully reported.'
                $scope.showError = false;
                $scope.showSuccess = true;
                $scope.user.cardIDAssigned = false;
                return deferred.resolve();
            }, function(response) {
                $scope.error = 'Reporting lost card failed.'
                $scope.profileUpdatePending = false;
                $scope.showError = true;
                $scope.showSuccess = false;
                return deferred.reject(response);
            });
            return deferred.promise

        }, function () {

          $log.info('Modal dismissed at: ' + new Date());
        });
    }

    $scope.changepassword = function() {
        $scope.passwordUpdatePending = true;
        var me = this;
        deferred = $q.defer();
        var pwdchange = {oldpassword:btoa($scope.pwd.oldpassword), newpassword:btoa($scope.pwd.password)};

        User.update(AuthService.getCurrentUserID(), pwdchange).then(function() {
            $scope.passwordUpdatePending = false;
            $scope.success = 'Password successfully changed.'
            $scope.showError = false;
            $scope.showSuccess = true;
            return deferred.resolve();
        }, function(response) {
            $scope.error = 'Changing password failed.'
            $scope.passwordUpdatePending = false;
            $scope.showError = true;
            $scope.showSuccess = false;
            return deferred.reject(response);
        });
        return deferred.promise
    }
})
