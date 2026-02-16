# Moneydance Open Source Extensions

Welcome to [The Infinite Kind's](https://infinitekind.com) repository of open source extensions and other utilities for Moneydance.

Here you will find all of the extensions which we, and others, have made available as open source for anyone to use or contribute towards.

To develop and build these extensions you'll need the Moneydance Developer Kit and documentation which is available at our [developer site](https://infinitekind.com/developer).

To communicate with the developers and other Moneydance community members, please feel free to join The Infinite Kind's [public slack](https://infinitekind.com/joinslack) or review the [extension development section of our support site](https://infinitekind.tenderapp.com/discussions/moneydance-development).

## Suggestions for building

* Use java version 17 or newer. When using a newer JDK, ideally set the target language/release to 17.
* kotlin has been enabled and you can build extensions using kotlin, java, or both. You should use the updated gradle build tools for this (inside the gradle folder)
* kotlin plugin should ideally be 1.9 with the same for API and language (match to the versions being used by Moneydance)
* Add `extadmin.jar` and `moneydance-dev.jar` from the devkit to the lib folder
* Some of the projects use the non-public api's. For those you need to copy the moneydance jar file to the lib directory
* Create keys as explained in the developer kit documentation (set keypass= in properties, and execute genkeys task)
