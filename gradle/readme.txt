Moneydance extension build system: can build java, kotlin, mixed java/kotlin, and python extensions

Built using gradle, with Groovy DSL file(s)

gradle installation dir: /gradle/
gradle main build file:	    build.gradle
gradle settings:	    settings.gradle
gradle properties:	    gradle.properties

user config file:	 /userconfig/user.gradle.properties

IntelliJ IDEA CE environment
- Project Structure: Project & Modules: JDK-21, Language level: 17
- Settings: Build, Execution, Deployment: Compiler
  - Kotlin Compiler, Compiler version: 1.9.21
  - Language version: 1.9, API version:	  1.9, Target JVM version: 17
- Settings: Build, Execution, Deployment: Build Tools: Gradle: Build and run using gradle

- gradle will auto-configure certain elements of the this project's IDEA settings
	- modules under MoneydanceOpen, one per feature (extension)
	- facets, one per feature (extension)
	- these are managed by gradle - no need to touch


Execute ./gradlew to show usage

TO START:
- edit user.gradle.properties and set keypass=xxx and then run genkeys; then build an extension
- Python packaging (with precompile) requires python2.7 installed
