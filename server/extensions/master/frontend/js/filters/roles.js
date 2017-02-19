/**
 * Created by drobisch on 02.02.16.
 */
RoseGuardenApp.filter('rolesFilter', function () {
    return function (type) {
        switch(type)
        {
            case 0:
                return "User";
            case 1:
                return "Admin"
            case 2:
                return "Supervisor"
            default:
                return "Invalid role";
        }
        return "None";
        // return firstNumber % secondNumber > 0
    };
});