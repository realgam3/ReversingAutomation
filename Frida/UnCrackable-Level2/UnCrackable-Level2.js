// https://github.com/realgam3/ReversingAutomation
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
                result = callback(result, args, this);
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

function getProcAddress(module, procName) {
    var imports = Module.enumerateImportsSync(module);
    for (var i = 0; i < imports.length; i++) {
        // console.log(imports[i].name);
        if (imports[i].name === procName) {
            return imports[i].address;
        }
    }
}

Java.perform(function () {
    // Bypass The Emulator Detection
    var Build = Java.use("android.os.Build");
    Build.TAGS.value = "release-keys";

    // Bypass The Root Detection
    hook("java.io.File", {
        function: "exists",
        callOriginal: true,
        callback: function (originalResult, args, self) {
            // console.log(self.path.value);
            if (self.path.value.endsWith("/su")) {
                return false;
            }
            if (["/system/app/Superuser.apk", "/system/xbin/daemonsu",
                "/system/etc/init.d/99SuperSUDaemon", "/system/bin/.ext/.su",
                "/system/etc/.has_su_daemon", "/system/etc/.installed_su_daemon",
                "/dev/com.koushikdutta.superuser.daemon/"].indexOf(self.path.value) !== -1) {
                return false;
            }
            return originalResult;
        }
    });

    var System = Java.use('java.lang.System');
    var ActivityThread = Java.use("android.app.ActivityThread");
    var AlertDialogBuilder = Java.use("android.app.AlertDialog$Builder");
    var DialogInterfaceOnClickListener = Java.use('android.content.DialogInterface$OnClickListener');
    Java.use("android.app.Activity").onCreate.overload("android.os.Bundle").implementation = function (savedInstanceState) {
        var currentActivity = this;

        // Get Main Activity
        var application = ActivityThread.currentApplication();
        var launcherIntent = application.getPackageManager().getLaunchIntentForPackage(application.getPackageName());
        var launchActivityInfo = launcherIntent.resolveActivityInfo(application.getPackageManager(), 0);

        // Alert Will Only Execute On Main Package Activity Creation
        var result = this.onCreate.overload("android.os.Bundle").call(this, savedInstanceState);
        if (launchActivityInfo.name.value === this.getComponentName().getClassName()) {
            // Alert Will Only Execute On Main Package Activity Creation
            if (launchActivityInfo.name.value === this.getComponentName().getClassName()) {
                var alert = AlertDialogBuilder.$new(this);
                alert.setMessage("Welcome To Viral Nights #2: \nReverse Engineering Automation");
                alert.setPositiveButton("Cool!", Java.registerClass({
                    name: 'il.co.realgame.OnClickListenerPositive',
                    implements: [DialogInterfaceOnClickListener],
                    methods: {
                        getName: function () {
                            return 'OnClickListenerPositive';
                        },
                        onClick: function (dialog, which) {
                            // Dismiss
                            dialog.dismiss();
                        }
                    }
                }).$new());

                alert.setNegativeButton("Booo! I'm Going Home!", Java.registerClass({
                    name: 'il.co.realgame.OnClickListenerNegative',
                    implements: [DialogInterfaceOnClickListener],
                    methods: {
                        getName: function () {
                            return 'OnClickListenerNegative';
                        },
                        onClick: function (dialog, which) {
                            // Close Application
                            currentActivity.finish();
                            System.exit(0);
                        }
                    }
                }).$new());

                // Create Alert
                alert.create().show();
            }

            // Hook strncmp Native Function
            var strncmp = getProcAddress("libfoo.so", "strncmp");
            // console.log(strncmp);
            Interceptor.attach(strncmp, {
                onEnter: function (args) {
                    this.str1 = args[0];
                    this.str2 = args[1];
                    this.num = args[2];
                },
                onLeave: function (retval) {
                    // Always Return True When The First String Size Is 23 And It Starts With "realgam3"
                    var num = this.num.toInt32();
                    if (Memory.readUtf8String(this.str1, num).startsWith("realgam3")) {
                        console.log("Original Password: " + Memory.readUtf8String(this.str2, num));
                        retval.replace(0);
                    }
                }
            });
        }
        return result;
    };
});
