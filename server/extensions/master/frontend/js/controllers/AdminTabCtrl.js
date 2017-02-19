RoseGuardenApp.controller('AdminTabCtrl', function ($scope, $location) {

    $scope.tabs = [
      { title : 'Settings', template : 'partials/admin/settings.html', glyphicon : 'glyphicon-cog'},
      { title : 'Users', active : true, template : 'partials/admin/users.html', glyphicon : 'glyphicon-user' },
      { title : 'Doors', template : 'partials/admin/doors.html', glyphicon : 'glyphicon-lock' },
      //{ title : 'Devices', template : 'partials/admin/devices.html'},
      { title : 'Log', template : 'partials/admin/log.html', glyphicon : 'glyphicon-list'},
      { title : 'Statistics', template : 'partials/admin/stats.html', glyphicon : 'glyphicon-stats'},
      { title : 'Debug', template : 'partials/admin/debug.html', glyphicon : 'glyphicon-exclamation-sign'}
    ];

    $scope.currentTab = $scope.tabs[1];

    $scope.onClickTab = function (tab) {
        $scope.currentTab.active = false;
        $scope.currentTab = tab;
        $scope.currentTab.active = true;
    }

})
