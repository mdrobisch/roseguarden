RoseGuardenApp.controller('MasterConfigCtrl', function($scope, ConfigService, $location) {

    var i=0;
    i++;
    var config = ConfigService.getConfig();

    function findConfigEntryByName(config, name) {
      for(var section in config) {
        if(typeof config[section] === 'object') {
            for (var i = 0; i < config[section].entries.length; i++) {
                if (config[section].entries[i].name == name)
                    return config[section].entries[i];
            }
        }
      }
    };
    //console.log(ConfigService.getConfig());

    $scope.nodeName = findConfigEntryByName(config, "NODE_NAME");
    $scope.nodePassword = findConfigEntryByName(config, "NODE_NAME");

    $scope.log = function () {
        console.log(config.node_config.entries[0]);
    };

});