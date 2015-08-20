RoseGuardenApp.controller('UserLogCtrl', function ($scope, $location, $q, AuthService, User) {


    var dates = [new Date("25 Dec, 1995 23:15:00"),new Date("1 Jan, 2005 13:15:00")];
    var names = ['Front door', 'ProtosV2'];
    var types = ['Opening door','Unlock device'];
    var usernames = ['Marcus Drobisch', 'Max Mustermann'];
    var usermails = ['m.drobisch@googlemail.com', 'Max.Mustermann@googlemail.com'];
    var authentificationTypes = [0, 1,0, 0];

    var id = 1;

    $scope.rowCollection = [];
    $scope.displayedCollection = [];

    function generateRandomItem(id) {

        var date = dates[Math.floor(Math.random() * 2)];
        var name = names[Math.floor(Math.random() * 2)];
        var type = types[Math.floor(Math.random() * 2)];
        var username = usernames[Math.floor(Math.random() * 2)];
        var usermail = usermails[Math.floor(Math.random() * 2)];
        var authentificationType = authentificationTypes[Math.floor(Math.random() * 2)];
        return {
            id: id,
            date: date,
            name: name,
            type: type,
            authentificationType: authentificationType,
            username: username,
            usermail: usermail
        };
    }

    function loadItemsDummy() {
        for (id; id < 19; id++) {
            $scope.rowCollection.push(generateRandomItem(id));
        }
        //copy the references (you could clone ie angular.copy but then have to go through a dirty checking for the matches)
        $scope.displayedCollection = [].concat($scope.rowCollection);
    }


    loadItemsDummy();

    //add to the real data holder
    $scope.addRandomItem = function addRandomItem() {
        $scope.rowCollection.push(generateRandomItem(id));
        id++;
    };

    //remove to the real data holder
    $scope.removeItem = function removeItem(row) {
        var index = $scope.rowCollection.indexOf(row);
        if (index !== -1) {
            $scope.rowCollection.splice(index, 1);
        }
    }
})