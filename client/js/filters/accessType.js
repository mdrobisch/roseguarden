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
            case 3:
                return "Lifetime access"
            case 4:
                return "Monthly day-budget";
            case 5:
                return "Quarterly day-budget";
            default:
                return "Invalid type";
        }
        return "None";
        // return firstNumber % secondNumber > 0
    };
});