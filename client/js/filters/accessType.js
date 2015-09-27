/**
 * Created by drobisch on 26.09.15.
 */
RoseGuardenApp.filter('accessTypeFilter', function () {
    return function (type) {
        switch(type)
        {
            case 0:
                return "No access";
            case 1:
                return "Access period"
            case 2:
                return "Access days"
            case 2:
                return "Lifetime access"
            default:
                return "Invalid type";
        }
        return "None";
        // return firstNumber % secondNumber > 0
    };
});