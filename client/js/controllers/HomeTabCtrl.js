RoseGuardenApp.controller('HomeTabCtrl', function ($scope, $location) {

    $scope.tabs = [
      { title : 'Profile', active : true, template : 'partials/user/profile.html', glyphicon : 'glyphicon-user'},
      { title : 'Log', template : 'partials/user/log.html', glyphicon : 'glyphicon-list'},
      { title : 'Admins', template : 'partials/user/adminsList.html', glyphicon : 'glyphicon-star-empty'}
    ];

    $scope.currentTab = $scope.tabs[0];

    $scope.onClickTab = function (tab) {
        $scope.currentTab.active = false;
        $scope.currentTab = tab;
        $scope.currentTab.active = true;
    }

})
