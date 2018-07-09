const { exec } = require('child_process');
const loaderUtils = require('loader-utils');
const fs = require('fs');
const os = require('os');
const path = require('path');

module.exports = function(source) {
    var callback = this.async();
    var options = loaderUtils.getOptions(this);
    var tmpFile = path.join(os.tmpdir(), "file_" + new Date().getTime() + ".css");
    fs.writeFileSync(tmpFile, source);
    var cmd = "css-flip" + " " + tmpFile;
    var command = exec(cmd, function(err, result) {
        if (err) return callback(err);
        callback(null, result);
        fs.unlinkSync(tmpFile);
    });

};
module.exports.raw = true;
