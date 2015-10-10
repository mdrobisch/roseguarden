/**
 * Created by drobisch on 08.10.15.
 */
RoseGuardenApp.factory('UserList', function(Restangular) {
    var UserList = {
        get: function (id, bypassErrorInterceptor) {
            return Restangular
                .all('users', id)
                .withHttpConfig({bypassErrorInterceptor: bypassErrorInterceptor})
                .getList();
        }
    };
    return UserList;

})
