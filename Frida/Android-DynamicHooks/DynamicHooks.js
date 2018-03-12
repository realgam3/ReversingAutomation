function hook(obj, options) {
    var Exception = Java.use('java.lang.Exception');
    var func = options['function'] !== undefined ? options['function'] : '$init';
    var args = options['arguments'] !== undefined ? options['arguments'] : [];
    var debug = options['debug'] !== undefined ? options['debug'] : false;
    var callOriginal = options['callOriginal'] !== undefined ? options['callOriginal'] : true;
    var callback = options['callback'] = options['callback'];

    try {
        Java.use(obj)[func].overload.apply(null, args).implementation = function () {
            var args = [].slice.call(arguments);
            var result = null;
            if (callOriginal) {
                result = this[func].apply(this, args);
            }
            if (callback) {
                result = callback(result, args);
            }


            if (debug) {
                var calledFrom = Exception.$new().getStackTrace().toString().split(',')[1];
                var message = JSON.stringify({
                    function: obj + "." + func,
                    arguments: args,
                    result: result,
                    calledFrom: calledFrom
                });
                console.log(obj + "." + func + "[\"Debug\"] => " + message);
            }

            return result;
        };
    } catch (err) {
        console.log(obj + "." + func + "[\"Error\"] => " + err);
    }
}

Java.perform(function () {
    hook("java.lang.Runtime", {
        function: "exec",
        arguments: ["java.lang.String"],
        debug: true,
        callOriginal: true,
        callback: function (originalResult, args) {
            console.log("Args: " + JSON.stringify(args));
            console.log("Result: " + originalResult);
            return originalResult;
        }
    });
});
