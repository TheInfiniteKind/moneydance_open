Moneydance extension build system: can build java, kotlin, mixed java/kotlin, and python extensions

Built using gradle (wrapper), with Groovy DSL file(s)

gradle installation dir: [ROOT], and /gradle
gradle main build file:	    build.gradle
gradle settings:	        settings.gradle
gradle properties:	        gradle.properties

user config file:	 /user.properties

machine config:      ~/.gradle/gradle.properties
                     org.gradle.java.home=/Library/Java/JavaVirtualMachines/temurin-25.jdk/Contents/Home
                     (to define the JVM that gradle wrapper will execute on)

IntelliJ IDEA CE environment
- Project Structure: Project & Modules: JDK-25, Language level: 17
- Settings: Build, Execution, Deployment: Compiler
  - Kotlin Compiler, Plugin, Compiler version: 2.3.21 (terminal version that supports kotlin language/api 1.9)
  - Language version: 1.9, API version:	  1.9, Target JVM version: 17
- Settings: Build, Execution, Deployment: Build Tools: Gradle: Build and run using gradle

- gradle (wrapper) will auto-configure certain elements of the this project's IDEA settings
	- modules under MoneydanceOpen, one per feature (extension)
	- facets, one per feature (extension)
	- these are managed by gradle - no need to touch


Execute ./gradlew to show usage

TO START:
- edit "user.properties" and set "extprivkeypass=xxx" and then run task "genKeys"; then build an extension
- Python packaging (with precompile) requires python2.7 installed
