/**
 * Created by drobisch on 04.11.15.
 */
RoseGuardenApp.controller('SendWelcomeMailCtrl', function ($scope, $modalInstance, $timeout, name, $log) {

  $scope.dt = new Date();
  $scope.name = name;


  $scope.open = function() {

    $timeout(function() {
      $scope.opened = true;
    });
  };


  $scope.ok = function (result) {
      $log.warn("ok")
    $modalInstance.close(result);
  };

  $scope.cancel = function () {
      $log.warn("dismiss")
    $modalInstance.dismiss('cancel');
  };

})