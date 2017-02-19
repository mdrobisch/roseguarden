RoseGuardenApp.controller('SupervisorUsersCtrl', function($scope,$modal, $log, $q, User, RfidTag, InvalidateAuthCardRequest) {

    var firstnames = ['Thomas', 'Marcus', 'Lischen', 'Stephanie'];
    var lastnames = ['Müller', 'Drobisch', 'Meier', 'Lehmann'];
    var mails = ['a@gmx.de', 'b@gmx.de', 'c@gmx.de', 'd@gmx.de'];
    var phones = ['0176 5345621', '0154 7537476', '0172 86586587', '0161 65758897'];
    var cardids = ['123.3.86.93', '', '221.96.63.87', '73.23.46.13'];
    var dates = [new Date("25 Dec, 2014 23:15:00"),new Date("1 Jan, 2015 13:15:00"),new Date("11 Mar, 2015 13:15:00"),new Date("5 Feb, 2015 13:15:00")];
    var times = [new Date(new Date().setHours(11,30,0,0)), new Date(new Date().setHours(10,30,0,0)),new Date(new Date().setHours(16,30,0,0)),new Date(new Date().setHours(15,30,0,0))];
    var daybudgets = [0, 4,5, 0];
    var accessdaytypes = [0, 1,2, 0];
    var budgets = [0.00,10.12,5,3.21];
    var validationDayMasks = [0x6F,0x6F,0x60,0x1F];
    var keyMasks = [0x03,0x01,0x08,0x06];
    var roles = [0, 1,0, 0];
    var id = 1;


    $scope.message = 'This is the AdminSpaceCtrl message';

    $scope.rfidtaginfo = "RFID tag. <br> Click to update.";
    $scope.rfidTagId = "";
    $scope.rfidTagUser = "";

    $scope.isLoading = true;
    $scope.showError = false;

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
        $scope.isLoading = false;
        //copy the references (you could clone ie angular.copy but then have to go through a dirty checking for the matches)
        $scope.displayedCollection = [].concat($scope.rowCollection);
    }

    function loadItemsFromAPI() {

        $scope.isLoading = true;
        deferred = $q.defer();
        User.getList(true).then(function(data) {
              console.log(data.length)
              for(i=0;i < data.length;i++) {
                  $scope.rowCollection.push(data[i]);
              }
            $scope.displayedCollection = [].concat($scope.rowCollection);
            $scope.isLoading = false;
            return deferred.resolve();
        }, function(response) {
            $scope.showError = false;
            return deferred.reject(response);
        });
        return deferred.promise


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

    loadItemsFromAPI();
    //loadItemsDummy();

    $scope.updateRfidInfo = function updateRfidInfo() {
        $scope.rfidtaginfo = "Request tag-info ..."
        deferred = $q.defer();
        RfidTag.getInfo(true).then(function(tagInfo) {
            console.log(tagInfo);


            $scope.rfidTagUser = tagInfo.userInfo;
            $scope.rfidTagId = tagInfo.tagId;

            // debug setting
            //console.error("Taginfo is in debug mode");
            //$scope.rfidTagId = "192.12.2.34";

            if($scope.rfidTagId == "")
            {
                $scope.rfidtaginfo = "No rfid-tag detected";
            }
            else
            {
                $scope.rfidtaginfo = $scope.rfidTagId + " <br>  " + $scope.rfidTagUser;
            }

            return deferred.resolve();
        }, function(response) {
            $scope.rfidtaginfo = "Error while request tag-info";
            return deferred.reject(response);
        });
        return deferred.promise;
    }

    //add to the real data holder
    $scope.addRandomItem = function addRandomItem() {
        $scope.rowCollection.push(generateRandomItem(id));
        id++;
    };


    $scope.assignUserRfidTag = function assignUserRfidTag(row) {
        console.log("Request rfid tag assign");
        $scope.showError = false;
        deferred = $q.defer();
        var assigndata = {email : row.email, rfidTagId : $scope.rfidTagId};

        RfidTag.postAssign(assigndata).then(function(response_data) {
            $log.info('Response  ' + response_data);
            $scope.dataLoading = false;
            $scope.showError = false;
            $scope.showSuccess = true;

            var index = $scope.rowCollection.indexOf(row);
            $scope.rowCollection[index].cardID = $scope.rfidTagId;


            return deferred.resolve();
        }, function(response) {
            $scope.error = 'Assign rfid tag falied' + ' (' + response.data + ' )'
            $scope.dataLoading = false;
            $scope.showSuccess = false;
            $scope.showError = true;
            return deferred.reject(response);
        });
        return deferred.promise;
    };

    $scope.invalidateUserRfidTag = function invalidateUserRfidTag(row) {

        var modalInstance = $modal.open({
              templateUrl: 'partials/modals/InvalidateRfidTag.html',
              controller: 'InvalidateRFIDCtrl',
              windowClass: 'center-modal',
              resolve: {
                name: function () {
                    return row.firstName + ' ' + row.lastName; }
              }
            });

        modalInstance.result.then(function (selected) {

            InvalidateAuthCardRequest.create(row.id).then(function() {
                $scope.profileUpdatePending = false;
                $scope.success = 'Lost card successfully reported.'
                $scope.showError = false;
                $scope.showSuccess = true;

                row.cardID = '';

                return deferred.resolve();
            }, function(response) {
                $scope.error = 'Reporting lost card failed.'
                $scope.profileUpdatePending = false;
                $scope.showError = true;
                $scope.showSuccess = false;
                return deferred.reject(response);
            });
            return deferred.promise

        }, function () {

          $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.withdrawUserRfidTag = function withdrawUserRfidTag(row) {
        console.log("Request rfid tag withdraw");
        $scope.showError = false;
        deferred = $q.defer();
        var withdrawdata = {email : row.email, rfidTagId : $scope.rfidTagId};

        RfidTag.postWithdraw(withdrawdata).then(function(response_data) {
            $log.info('Response  ' + response_data);
            $scope.dataLoading = false;
            $scope.showError = false;
            $scope.showSuccess = true;
            var index = $scope.rowCollection.indexOf(row);
            $scope.rowCollection[index].cardID = "";
            return deferred.resolve();
        }, function(response) {
            $scope.error = 'Assign rfid tag falied' + ' (' + response.data + ' )'
            $scope.dataLoading = false;
            $scope.showSuccess = false;
            $scope.showError = true;
            return deferred.reject(response);
        });
        return deferred.promise;
    };

    $scope.setupUserAccess = function setupUserAccess(row) {

        var modalInstance = $modal.open({
          templateUrl: 'partials/modals/SetupUserAccess.html',
          controller: 'SetupUserAccessCtrl',
          windowClass: 'center-modal',
          resolve: {
            selectedUser: function () {
                return row;
            }
          }
        });

        modalInstance.result.then(function (setupdata) {

            row.userUpdatePending = true;

            var setupaccess = {keyMask: setupdata.keyMask, accessDaysMask : setupdata.accessDaysMask,
                                accessDateStart : new Date(setupdata.accessDateStart), accessDateEnd : new Date(setupdata.accessDateEnd),
                                accessTimeStart : new Date(setupdata.accessTimeStart), accessTimeEnd : new Date(setupdata.accessTimeEnd),
                                accessType : setupdata.accessType, accessDayCounter : setupdata.accessDayCounter, accessDayCyclicBudget : setupdata.accessDayCyclicBudget};

            User.update(row.id, setupaccess).then(function() {
                $scope.profileUpdatePending = false;
                $scope.success = 'Successfully setup access.';
                $scope.showError = false;
                $scope.showSuccess = true;

                var index = $scope.rowCollection.indexOf(row);
                $scope.rowCollection[index].keyMask = setupdata.keyMask;
                $scope.rowCollection[index].accessDaysMask = setupdata.accessDaysMask;
                $scope.rowCollection[index].accessDateStart = setupdata.accessDateStart;
                $scope.rowCollection[index].accessDateEnd = setupdata.accessDateEnd;
                $scope.rowCollection[index].accessTimeStart = setupdata.accessTimeStart;
                $scope.rowCollection[index].accessTimeEnd = setupdata.accessTimeEnd;
                $scope.rowCollection[index].accessType = setupdata.accessType;
                $scope.rowCollection[index].accessDayCounter = setupdata.accessDayCounter;
                $scope.rowCollection[index].accessDayCyclicBudget = setupdata.accessDayCyclicBudget;

                row.userUpdatePending = false;

                return deferred.resolve();
            }, function(response) {
                $scope.error = 'Setup user access failed.';
                $scope.profileUpdatePending = false;
                $scope.showError = true;
                $scope.showSuccess = false;

                row.userUpdatePending = false;

                return deferred.reject(response);
            });
            return deferred.promise

        }, function () {
          row.userUpdatePending = false;
          $log.info('Modal dismissed at: ' + new Date());
        });
    };

    //remove to the real data holder
    $scope.removeUser = function removeUser(row) {

        var modalInstance = $modal.open({
          templateUrl: 'partials/modals/RemoveUser.html',
          controller: 'RemoveUserCtrl',
          windowClass: 'center-modal',
          resolve: {
            name: function () {
                return row.firstName + ' ' + row.lastName; }
          }
        });

        modalInstance.result.then(function (selected) {
            var index = $scope.rowCollection.indexOf(row);
            if (index !== -1) {

                User.delete(row.id).then(function() {
                    $scope.profileUpdatePending = false;
                    $scope.success = 'User successfully removed.'
                    $scope.showError = false;
                    $scope.showSuccess = true;

                    $scope.rowCollection.splice(index, 1);
                    return deferred.resolve();
                }, function(response) {
                    $scope.error = 'Removing user failed.'
                    $scope.profileUpdatePending = false;
                    $scope.showError = true;
                    $scope.showSuccess = false;
                    return deferred.reject(response);
                });
                return deferred.promise
            }

        }, function () {
          $log.info('Modal dismissed at: ' + new Date());
        });


    }
})