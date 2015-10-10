RoseGuardenApp.controller('AdminUsersCtrl', function($scope,$modal, $log) {

    $scope.message = 'This is the AdminSpaceCtrl message';
    var firstnames = ['Thomas', 'Marcus', 'Lischen', 'Stephanie'];
    var lastnames = ['Müller', 'Drobisch', 'Meier', 'Lehmann'];
    var mails = ['a@gmx.de', 'b@gmx.de', 'c@gmx.de', 'd@gmx.de'];
    var phones = ['0176 5345621', '0154 7537476', '0172 86586587', '0161 65758897'];
    var cardids = ['123.3.86.93', '', '221.96.63.87', '73.23.46.13'];
    var dates = [new Date("25 Dec, 2014 23:15:00"),new Date("1 Jan, 2015 13:15:00"),new Date("11 Mar, 2015 13:15:00"),new Date("5 Feb, 2015 13:15:00")];
    var times = [new Date(new Date().setHours(11,30,0,0)), new Date(new Date().setHours(10,30,0,0)),new Date(new Date().setHours(16,30,0,0)),new Date(new Date().setHours(15,30,0,0))]
    var daybudgets = [0, 4,5, 0];
    var accessdaytypes = [0, 1,2, 0];
    var budgets = [0.00,10.12,5,3.21];
    var validationDayMasks = [0x6F,0x6F,0x60,0x1F]
    var keyMasks = [0x03,0x01,0x08,0x06]
    var roles = [0, 1,0, 0];
    var id = 1;

    $scope.rowCollection = [];
    $scope.displayedCollection = [];

    function generateRandomItem(id) {

        var firstname = firstnames[Math.floor(Math.random() * 3)];
        var lastname = lastnames[Math.floor(Math.random() * 3)];
        var mail = mails[Math.floor(Math.random() * 3)];
        var phone = phones[Math.floor(Math.random() * 3)];
        var card = cardids[Math.floor(Math.random() * 3)];
        var role = roles[Math.floor(Math.random() * 3)];
        var licenseMask = keyMasks[Math.floor(Math.random() * 3)];
        var keyMask = keyMasks[Math.floor(Math.random() * 3)];
        var registrationDate = dates[Math.floor(Math.random() * 3)];
        var lastLoginDate = dates[Math.floor(Math.random() * 3)];
        var validateType = accessdaytypes[Math.floor(Math.random() * 2)];
        var validateDayCounter = daybudgets[Math.floor(Math.random() * 3)];
        var validationDateStart = dates[Math.floor(Math.random() * 3)];
        var validationDateEnd = dates[Math.floor(Math.random() * 3)];
        var validationDaysMask = validationDayMasks[Math.floor(Math.random() * 3)];
        var validationTimeStart = times[Math.floor(Math.random() * 3)];
        var validationTimeEnd = times[Math.floor(Math.random() * 3)];
        var budget = budgets[Math.floor(Math.random() * 3)];

        return {
            id: id,
            firstName: firstname,
            lastName: lastname,
            mail: mail,
            phone: phone,
            cardID: card,
            role: role,
            licenseMask: licenseMask,
            keyMask: keyMask,
            registrationDate: registrationDate,
            lastLoginDate: lastLoginDate,
            accessType: validateType,
            accessDateStart: validationDateStart,
            accessDateEnd: validationDateEnd,
            accessDaysMask: validationDaysMask,
            accessTimeStart: validationTimeStart,
            accessTimeEnd: validationTimeEnd,
            accessDayCounter: validateDayCounter,
            budget: budget
        };
    }

    function loadItemsDummy() {
        for (id=0; id < 3; id++) {
            $scope.rowCollection.push(generateRandomItem(id));
        }
        //copy the references (you could clone ie angular.copy but then have to go through a dirty checking for the matches)
        $scope.displayedCollection = [].concat($scope.rowCollection);
    }

    function loadItemsFromAPI() {
        $http.get('//127.0.0.1:5000/Users').
            success(function(data) {
              console.log(data.length);
              for(i=0;i < data.length;i++) {
                  $scope.rowCollection.push({
                        id : data[i].id,
                        firstName : data[i].first_name,
                        lastName : data[i].last_name,
                        mail : data[i].mail,
                        phone : data[i].phone,
                        cardid : data[i].card_id});
              }
            });

        $scope.displayedCollection = [].concat($scope.rowCollection);

        /*
        $http({
            method: 'GET',
            url: 'http://localhost:5000/Users'
        })
        .success(function (data, status, headers, config) {
            $scope.rowCollection.push(generateRandomItem(id));

            // successful data retrieval
        })
        .error(function (data, status, headers, config) {
        // something went wrong :(
        });
        */
    }

    //loadItemsFromAPI();
    loadItemsDummy();

    //add to the real data holder
    $scope.addRandomItem = function addRandomItem() {
        $scope.rowCollection.push(generateRandomItem(id));
        id++;
    };

    //remove to the real data holder
    $scope.removeItem = function removeItem(row) {

        var modalInstance = $modal.open({
          templateUrl: 'partials/modals/RemoveUser.html',
          controller: 'RemoveUserCtrl',
          windowClass: 'center-modal',
          resolve: {
            name: function () {
                return row.firstName + ' ' + row.lastName;
          }
       }
        });

        modalInstance.result.then(function (selected) {
            var index = $scope.rowCollection.indexOf(row);
            if (index !== -1) {
                $scope.rowCollection.splice(index, 1);
            }

        }, function () {
          $log.info('Modal dismissed at: ' + new Date());
        });


    }
})