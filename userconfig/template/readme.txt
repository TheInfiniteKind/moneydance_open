Moneydance extension build system
The [ROOT] "/userconfig" folder and its file(s) belongs to the MoneydanceOpen project which is used to compile, package, and sign extensions.
These files are used by gradle during the build process. The gradle (wrapper) files are contained in [ROOT], and "/gradle" folders.

It's possible that you already have user.properties config files in the [ROOT]/ and/or [ROOT]/src folder(s) if you have an existing build system setup.
If so, they will automatically be used by this build system.

If you don't already have a user.properties file, there is a sample file in "userconfig/user.properties-sample" which you can copy to either [ROOT]/ or userconfig/ folder named 'user.properties' as a starting point

It should contain as a minimum the following entry:

extprivkeypass=secret

where secret would be replaced by a passphrase of your choosing.

This passphrase should be used when running the following from the project's root folder:

./gradlew genKeys

which will create the following files (in this "/userconfig" folder):

priv_key
pub_key

These two files are also used when building extensions. They sign your extension using your passphrase and key.

ADVANCED:
you can optionally add the following setting to your user.properties file

md_ext_lib_dir=path

where path is the folder path to a folder containing a full set of Moneydance jars that should be used instead of the default 
set of jars in the /lib/ folder.

DO NOT ATTEMPT to set gradle system properties here (e.g. org.gradle.parallel=false) as these will be ignored.
To do this you have to update "gradle.properties" found in project's root folder


