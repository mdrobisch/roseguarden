RoseGuardenApp.controller('SupervisorTabCtrl', function ($scope, $location) {

    $scope.tabs = [
      { title : 'Users', active : true, template : 'partials/supervisor/users.html', glyphicon : 'glyphicon-user' },
      { title : 'Debug', template : 'partials/admin/debug.html', glyphicon : 'glyphicon-exclamation-sign'}
    ];

    $scope.currentTab = $scope.tabs[0];

    $scope.onClickTab = function (tab) {
        $scope.currentTab.active = false;
        $scope.currentTab = tab;
        $scope.currentTab.active = true;
    }

})
