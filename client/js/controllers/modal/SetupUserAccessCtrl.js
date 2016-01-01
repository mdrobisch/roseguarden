/**
 * Created by drobisch on 15.10.15.
 */
RoseGuardenApp.controller('SetupUserAccessCtrl', function ($scope, $modalInstance, $log, $timeout, selectedUser) {

  $scope.dt = new Date();
  $scope.name = name;

  $scope.input = { num: 0   };
  $scope.AccessTypevalues = ["No access","Access period","Access days","Lifetime access", "Monthly day-budget", "Quarterly day-budget", ];
  $scope.selectedAccessType = selectedUser.accessType;

  $scope.accesDaysMaskMon =  (selectedUser.accessDaysMask & 0x01) != 0;
  $scope.accesDaysMaskTue =  (selectedUser.accessDaysMask & 0x02) != 0;
  $scope.accesDaysMaskWed =  (selectedUser.accessDaysMask & 0x04) != 0;
  $scope.accesDaysMaskThu =  (selectedUser.accessDaysMask & 0x08) != 0;
  $scope.accesDaysMaskFri =  (selectedUser.accessDaysMask & 0x10) != 0;
  $scope.accesDaysMaskSat =  (selectedUser.accessDaysMask & 0x20) != 0;
  $scope.accesDaysMaskSun =  (selectedUser.accessDaysMask & 0x40) != 0;

  $scope.keyMaskRed       =  (selectedUser.keyMask & 0x01) != 0;
  $scope.keyMaskGreen     =  (selectedUser.keyMask & 0x02) != 0;
  $scope.keyMaskBlack     =  (selectedUser.keyMask & 0x04) != 0;
  $scope.keyMaskPink      =  (selectedUser.keyMask & 0x08) != 0;
  $scope.keyMaskMarine    =  (selectedUser.keyMask & 0x10) != 0;
  $scope.keyMaskOrange    =  (selectedUser.keyMask & 0x20) != 0;
  $scope.keyMaskOlive     =  (selectedUser.keyMask & 0x40) != 0;
  $scope.keyMaskPurple    =  (selectedUser.keyMask & 0x80) != 0;

  $scope.accesDateStart = new Date(selectedUser.accessDateStart);
  $scope.accesDateEnd = new Date(selectedUser.accessDateEnd);

  $scope.accessDayCounter = selectedUser.accessDayCounter;

  $scope.accessDayCyclicBudget = selectedUser.accessDayCyclicBudget;

  $scope.accesTimeStart = moment(new Date(selectedUser.accessTimeStart));
  $scope.accesTimeStart_display = $scope.accesTimeStart.subtract($scope.accesTimeStart.utcOffset(),"minute");

  $scope.accesTimeEnd = moment(new Date(selectedUser.accessTimeEnd));
  $scope.accesTimeEnd_display = $scope.accesTimeEnd.subtract($scope.accesTimeEnd.utcOffset(),"minute");


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

  $scope.accesTime_changed = function() {
    $scope.accesTimeStart = moment($scope.accesTimeStart_display).add($scope.accesTimeStart.utcOffset(),"minute");
    $scope.accesTimeEnd = moment($scope.accesTimeEnd_display).add($scope.accesTimeEnd.utcOffset(),"minute");
  };

  $scope.ok = function () {
    var keyMask = 0;
    if($scope.keyMaskRed)
      keyMask |= 0x01;
    if($scope.keyMaskGreen)
      keyMask |= 0x02;
    if($scope.keyMaskBlack)
      keyMask |= 0x04;
    if($scope.keyMaskPink)
      keyMask |= 0x08;
    if($scope.keyMaskMarine)
      keyMask |= 0x10;
    if($scope.keyMaskOrange)
      keyMask |= 0x20;
    if($scope.keyMaskOlive)
      keyMask |= 0x40;
    if($scope.keyMaskPurple)
      keyMask |= 0x80;

    var accesDaysMask = 0;
    if($scope.accesDaysMaskMon)
      accesDaysMask |= 0x01;
    if($scope.accesDaysMaskTue)
      accesDaysMask |= 0x02;
    if($scope.accesDaysMaskWed)
      accesDaysMask |= 0x04;
    if($scope.accesDaysMaskThu)
      accesDaysMask |= 0x08;
    if($scope.accesDaysMaskFri)
      accesDaysMask |= 0x10;
    if($scope.accesDaysMaskSat)
      accesDaysMask |= 0x20;
    if($scope.accesDaysMaskSun)
      accesDaysMask |= 0x40;

    $scope.accesTimeStart = moment($scope.accesTimeStart_display).add($scope.accesTimeStart.utcOffset(),"minute");
    $scope.accesTimeEnd = moment($scope.accesTimeEnd_display).add($scope.accesTimeEnd.utcOffset(),"minute");

    $modalInstance.close( { accessDateStart : $scope.accesDateStart, accessDateEnd : $scope.accesDateEnd,
                            accessTimeStart : $scope.accesTimeStart , accessTimeEnd : $scope.accesTimeEnd,
                            accessDayCounter: $scope.accessDayCounter , accessType : $scope.selectedAccessType,
                            keyMask : keyMask, accessDaysMask : accesDaysMask , accessDayCyclicBudget : $scope.accessDayCyclicBudget});
  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };

})