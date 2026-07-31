/*
 * Author: Stuart Beesley - February 2026
 * usage.gradle.kts: gradle buildfile that simply displays usage information for this build set
 * This should not be run standalone
*/
val p: Project = project

if (!p.extra.has("executingMainBuild")) { throw GradleException("usage.gradle must be applied from [ROOT]/build.gradle, not executed standalone!") }

tasks.register("printUsage") {
  doLast {
    logger.lifecycle("")
    logger.lifecycle("-------------------------------------------------------------------------------------------------------------------------")
    logger.lifecycle("Moneydance Gradle (wrapper) build - usage")
    logger.lifecycle("")
    logger.lifecycle("./gradlew verifyConfig         -> configuration + path checks (default)")
    logger.lifecycle("./gradlew <extensionname>      -> build & sign one extension - e.g. ")
    logger.lifecycle("./gradlew allJavaKotlin        -> build all Java/Kotlin extensions")
    logger.lifecycle("./gradlew allPython            -> build all Python extensions")
    logger.lifecycle("./gradlew all                  -> build everything")
    logger.lifecycle("./gradlew clean                -> removes the dist folder, and all build/compiled files")
    logger.lifecycle("./gradlew cleanextensionname   -> cleanup a single extension's build files")
    logger.lifecycle("./gradlew ensureDist           -> ensure the dist folder is present (otherwise does nothing)")
    logger.lifecycle("./gradlew ensureUserConfig     -> ensure the userconfig folder is present (otherwise does nothing)")
    logger.lifecycle("./gradlew newUserInit          -> create new user properties config (prompts to overwrite)")
    logger.lifecycle("./gradlew genKeys              -> generate signing keys (set extprivkeypass= in user.properties first)")
    logger.lifecycle("")
    logger.lifecycle("User override / configuration files (in order of precedence):")
    logger.lifecycle("  1. system property  : 'moneydance_key_pass'   (extprivkeypass only)")
    logger.lifecycle("  2. environment var  : 'MONEYDANCE_KEY_PASS'   (extprivkeypass only)")
    logger.lifecycle("  3. [ROOT]/user.properties                     (legacy filename)                gitignored")
    logger.lifecycle("  4. [ROOT]/src/user.properties                 (legacy filename)                gitignored")
    logger.lifecycle("  9. [ROOT]/gradle.properties                   (base properties)                committed to git")
    logger.lifecycle("")
    logger.lifecycle("Signing setup:")
    logger.lifecycle("  Set extprivkeypass=<your passphrase> in user.properties")
    logger.lifecycle("  Then run: ./gradlew genKeys")
    logger.lifecycle("")
    logger.lifecycle("Optional flags (user.properties):")
    logger.lifecycle("  debug=true                   -> enable additional debug messages")
    logger.lifecycle("  md_ext_lib_dir=<folder>      -> specify folder containing a 'master set' of Moneydance jars (overriding lib folder jars)")
    logger.lifecycle("")
    logger.lifecycle("-------------------------------------------------------------------------------------------------------------------------")
    logger.lifecycle("")
  }
}