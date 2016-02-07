RoseGuardenApp.controller('ApplicationCtrl', function($scope, $location, AuthService) {

    $scope.$on('$routeChangeStart', function (event, next) {

        if (AuthService.isAdmin()) {
            $scope.isAdmin = true;
        } else {
            $scope.isAdmin = false;
        }

        if (AuthService.isSupervisor()) {
            $scope.isSupervisor = true;
        } else {
            $scope.isSupervisor = false;
        }


        if($location.path() === "/logout") {
            $scope.isLoggedIn = false;
        }

        if($location.path() === "/") {
            $scope.isLoggedIn = AuthService.isAuthenticated();
        }

    });
    $scope.isActive = function(path) {
        if ($location.path().substr(0, path.length) === path) {
            if (path === "/" && $location.path() === "/") {
                return true;
            } else if (path === "/") {
                return false;
            } else {
                return true;
            }
        } else {
            return false;
        }
    };

})