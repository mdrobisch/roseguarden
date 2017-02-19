/**
 * Created by drobisch on 20.10.15.
 */

RoseGuardenApp.controller('AdminSettingsCtrl', function($scope,$log, $q, Setting) {

    $scope.isLoading = true;
    $scope.showError = false;
    $scope.showInfo = false;
    $scope.settingCollection = new Array();
    $scope.settingsAvailable = false;

    $scope.formModel_keyMask = [];

    function updateForm() {
        $scope.formModel_keyMask = [];
        console.log($scope.settingCollection["NODE_VALID_KEYS_MASK"]);
        validKeyMask = parseInt($scope.settingCollection["NODE_VALID_KEYS_MASK"].value);
        for(var i = 0;i < 8; i++) {
            if ( ((0x01 << i) & validKeyMask) != 0)
                $scope.formModel_keyMask.push(true);
            else
                $scope.formModel_keyMask.push(false);
        }
    }

    function updateSetting(newSetting, oldSetting) {
        $scope.settingsUpdatePending = true;
        $scope.showSuccess = false;
        $scope.showInfo = false;
        deferred = $q.defer();
        Setting.update(newSetting.id, newSetting).then(function() {
            $scope.settingsUpdatePending = false;
            $scope.settingCollection[oldSetting.name] = newSetting;
            $scope.success = 'Setting successfully changed.';
            $scope.showError = false;
            $scope.showSuccess = true;
            updateForm();
            return deferred.resolve();
        }, function(response) {
            $scope.error = 'Updating setting failed.'
            $scope.settingCollection[oldSetting.name] = oldSetting;
            $scope.settingsUpdatePending = false;
            $scope.showError = true;
            $scope.showSuccess = false;
            updateForm();
            return deferred.reject(response);
        });
        return deferred.promise
    }



    $scope.updateKeyMaskSettings = function() {
        var oldsetting = $scope.settingCollection["NODE_VALID_KEYS_MASK"];
        var newSetting = Setting.clone(oldsetting);

        keyMask = 0;
        for(var i = 0; i < 8; i++) {
            if ($scope.formModel_keyMask[i] == true){
                keyMask = keyMask | (0x01 << i);
            }
        }
        newSetting.value = keyMask.toString();
        updateSetting(newSetting, oldsetting);

    };


    function loadItemsFromAPI() {

        $scope.isLoading = true;
        deferred = $q.defer();
        Setting.getList(true).then(function(data) {

            $scope.showError = false;
            if(data.length > 0) {
                $scope.settingsAvailable = true;
                for (i = 0; i < data.length; i++) {
                    $scope.settingCollection[data[i].name] = data[i];
                }
                updateForm();
            } else {
                $scope.statsAvailable = false;
                $scope.showInfo = true;
                $scope.info = "Not settings available.";
            }
            $scope.isLoading = false;

            return deferred.resolve();
        }, function(response) {
            $scope.error = "Unable to request settings. Please try again.";
            $scope.isLoading = false;
            $scope.showError = true;
            return deferred.reject(response);
        });
        return deferred.promise
    }

    loadItemsFromAPI();
});
