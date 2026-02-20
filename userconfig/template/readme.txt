Moneydance extension build system
The [ROOT] "/userconfig" folder and its file(s) belongs to the MoneydanceOpen project which is used to compile, package, and sign extensions.
These files are used by gradle during the build process. The gradle (wrapper) files are contained in [ROOT], and "/gradle" folders.
"user.gradle.properties" is a user-specific file that overrides settings used during the gradle build process

It's possible that you might have user config files in [ROOT]/ and/or [ROOT]/src folder(s) if you have an existing build system setup. These
might be called 'user.properties' (legacy), or 'user.gradle.properties'. Files in locations other than /userconfig take precedence.

REFER to the following file as an example: "/userconfig/template/user.gradle.properties"

You should start by creating a plain text file called: 

/userconfig/user.gradle.properties

It should contain as a minimum the following entry:

keypass=secret

where secret would be replaced by a passphrase of your choosing.

This passphrase should be used when running the following from the project's root folder:

./gradlew genKeys

which will create the following files (in this "/userconfig" folder):

priv_key
pub_key

These two files are also used when building extensions. They sign your extension using your passphrase and key.

NOTE: If you were previously using the Ant process, you can either leave your settings were they were, or relocate them
to "/userconfig" folder and then review the "user.gradle.properties" file (reconfirm any paths that were set and their relative locations to project root)


ADVANCED:
you can optionally add the following setting to user.gradle.properties

md_ext_lib_dir=path

where path is the folder path to a folder containing a full set of Moneydance jars that should be used instead of the default 
set of jars in the /lib/ folder.

DO NOT ATTEMPT to set gradle system properties here (e.g. org.gradle.parallel=false) as these will be ignored.
To do this you have to update "gradle.properties" found in project's root folder






