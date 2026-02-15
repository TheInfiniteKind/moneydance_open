Moneydance extension build system
The /userconfig/ folder and its file(s) belongs to the MoneydanceOpen project which is used to compile, package, and sign extensions.
These files are used by gradle during the build process. The gradle files are contained in the /gradle/ folder.
user.gradle.properties is a user-specific file that overrides settings used during the gradle build process

REFER to the following file as an example: /userconfig/template/user.gradle.properties

You should start by creating a plain text file called: 

/userconfig/user.gradle.properties

It should contain as a minimum the following entry:

keypass=secret

where secret would be replaced by a passphrase of your choosing.

This passphrase should be used when running:

/gradle/gradlew genkeys 

which will create the following files (in this /userconfig folder):

priv_key
pub_key

These two files are also used when building extensions. They sign your extension using your passphrase and key.

NOTE: If you were previously using the Ant process, then just run the following to create these files for you:
/gradle/gradlew migrateAntUserConfig

and then review the user.gradle.properties file.


ADVANCED:
you can optionally add the following setting to user.gradle.properties

mdbuildlibs=path

where path is the folder path to a folder containing a full set of Moneydance jars that should be used instead of the default 
set of jars in the /lib/ folder.

DO NOT ATTEMPT to set gradle system properties here (e.g. org.gradle.parallel=false) as these will be ignored.
To do this you have to update /gradle/gradle.properties






