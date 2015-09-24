#!/bin/bash
set -e

# Converts a Jython standalone jar into something usable with Java Web Start
JAR_PATH=$1
if [ -z $JAR_PATH ]; then
  JAR_PATH="lib/jython-2_7.jar"
fi

# Unix sucks at abspath resolution; ref http://stackoverflow.com/questions/3915040
JAR_PATH="$(cd "$(dirname "$JAR_PATH")"; pwd)/$(basename "$JAR_PATH")"

TEMPDIR=$(mktemp -d -t jarconv)
pushd "$TEMPDIR"
jar xf "$JAR_PATH"
rm -rf Lib/test  # including Jython's own unit tests is pointless
java -jar "$JAR_PATH" -m compileall Lib
find Lib -name "*.py" -delete
mv Lib/* .
rmdir Lib
jar cfm "$JAR_PATH" META-INF/MANIFEST.MF *
rm -rf "$TEMPDIR"
popd
