#!/bin/bash
set -e

# Converts a Jython standalone jar into something usable with Java Web Start
if [ -z $1 ]; then
  echo "Please give the path to the standalone jar as the first argument."
  exit 1
fi

CURRDIR=$(pwd)
JAR_PATH="$1"

CONVERTED_JAR_PATH="$CURRDIR/jython-webstart.jar"
TEMPDIR=$(mktemp -d)
cd "$TEMPDIR"
jar xf "$JAR_PATH"
rm -rf Lib/test  # including Jython's own unit tests is pointless
java -jar "$JAR_PATH" -m compileall Lib
find Lib -name "*.py" -delete
mv Lib/* .
rmdir Lib
jar cfm "$CONVERTED_JAR_PATH" META-INF/MANIFEST.MF *
rm -rf "$TEMPDIR"
