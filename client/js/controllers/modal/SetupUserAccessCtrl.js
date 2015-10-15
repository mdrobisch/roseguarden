/**
 * Created by drobisch on 15.10.15.
 */
RoseGuardenApp.controller('SetupUserAccessCtrl', function ($scope, $modalInstance, $timeout, name) {

  $scope.dt = new Date();
  $scope.name = name;

  $scope.input = { num: 0   };
  $scope.AccessTypevalues = ["No access","Access period","Access days","Lifetime access"];
  $scope.selectedAccessType = 0;


  $scope.mytime = new Date(99,5,24,0,0,0,0);

  $scope.hstep = 1;
  $scope.mstep = 15;

  $scope.options = {
    hstep: [1, 2, 3],
    mstep: [1, 5, 10, 15, 25, 30]
  };

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