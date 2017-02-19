/**
 * Created by drobisch on 21.02.16.
 */
RoseGuardenApp.factory('Setting', function(Restangular) {
    var Setting;
    Setting = {
        getList: function (bypassErrorInterceptor) {
            return Restangular
                .all('settings')
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .getList();
        },
        update: function(id,data) {
            return Restangular
                .one('setting', id)
                .withHttpConfig({bypassErrorInterceptor: true})
                .customPOST(data);
        },
        clone: function(setting) {
            var clonedSetting = {
                "id"    : setting.id,
                "name"  : setting.name,
                "type"  : setting.type,
                "value" : setting.value
            };
            return clonedSetting;
        }
    };
    return Setting;
})