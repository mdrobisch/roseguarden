/**
 * Created by drobisch on 02.08.15.
 */
RoseGuardenApp.filter('bitwiseAndFilter', function () {
    return function (firstNumber, secondNumber) {
        return ((parseInt(firstNumber, 10) & parseInt(secondNumber, 10)) === parseInt(secondNumber, 10));
        // return firstNumber % secondNumber > 0
    };
});