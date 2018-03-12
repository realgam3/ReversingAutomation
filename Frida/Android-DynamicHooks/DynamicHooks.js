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
            // Call Origin Function If True
            if (callOriginal) {
                result = this[func].apply(this, args);
            }
            // Call Callback If Exist
            if (callback) {
                result = callback(result, args);
            }
            // Debug Log
            if (debug) {
                var calledFrom = Exception.$new().getStackTrace().toString().split(',')[1];
                var message = JSON.stringify({
                    arguments: args,
                    result: result,
                    calledFrom: calledFrom
                });
                console.log(obj + "." + func + "[\"Debug\"] => " + message);
            }
            // Return Result
            return result;
        };
    } catch (err) {
        // Error Log
        console.log(obj + "." + func + "[\"Error\"] => " + err);
    }
}

// Example Usage
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
