RoseGuardenApp.controller('LogoutCtrl', function($scope, $location, Session, AuthService) {

    AuthService.logout();

})