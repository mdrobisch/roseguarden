RoseGuardenApp.controller('AdminTabCtrl', function ($scope, $location) {

    $scope.tabs = [
      //{ title : 'Settings', template : 'partials/admin/settings.html'},
      { title : 'Users', active : true, template : 'partials/admin/users.html', glyphicon : 'glyphicon-user' },
      { title : 'Doors', template : 'partials/admin/doors.html', glyphicon : 'glyphicon-lock' },
      //{ title : 'Devices', template : 'partials/admin/devices.html'},
      { title : 'Log', template : 'partials/admin/log.html', glyphicon : 'glyphicon-list'}
    ];

    $scope.currentTab = $scope.tabs[0];

    $scope.onClickTab = function (tab) {
        $scope.currentTab.active = false;
        $scope.currentTab = tab;
        $scope.currentTab.active = true;
    }

})
