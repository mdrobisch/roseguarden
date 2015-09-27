/**
 * Created by drobisch on 26.09.15.
 */
RoseGuardenApp.filter('weekdaysBitwiseFilter', function () {
    return function (bitcode) {
        var res = ""
        if(bitcode == 0)
            return "None";
        if((bitcode & 0x01) != 0)
            res += "Mo, "
        if((bitcode & 0x02) != 0)
            res += "Tu, "
        if((bitcode & 0x04) != 0)
            res += "We, "
        if((bitcode & 0x08) != 0)
            res += "Th, "
        if((bitcode & 0x10) != 0)
            res += "Fr, "
        if((bitcode & 0x20) != 0)
            res += "Sa, "
        if((bitcode & 0x40) != 0)
            res += "Su, "
        res = res.substring(0,res.length-2)
        return res;
    };
});