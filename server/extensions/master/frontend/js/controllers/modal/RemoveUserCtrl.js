/**
 * Created by drobisch on 02.08.15.
 */
RoseGuardenApp.controller('RemoveUserCtrl', function ($scope, $modalInstance, $timeout, name) {

  $scope.dt = new Date();
  $scope.name = name;


  $scope.open = function() {

    $timeout(function() {
      $scope.opened = true;
    });
  };


  $scope.ok = function () {
    $modalInstance.close($scope.dt);
  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };

})