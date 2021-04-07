InfiniteKind - Moneydance Python extensions

Documented by Stuart Beesley - StuWareSoftSystems 2021 - https://yogi1967.github.io/MoneydancePythonScripts/

NOTES ABOUT PYTHON EXTENSIONS:

- You want to be on Moneydance version 2021.1 build 3056 onwards as this is when Py extensions became 'fully functional'
- You can do anything in Python that a Java extension can do.

- Python extensions have to be executed by the Python Interpreter. This consumes 200-300MB of RAM. Clearly an overhead over compiled Java
- It's quicker to write Python over Java, and needs no compile, so you can very easily test within Moneybot
- Really you are using Jython(2.7). This is Java based with full access to Moneydance's 'internals'. You can do anything that a pure Java app could do.
- However, Python extensions have 'oddities' in how they are handled because of the way they are implemented in Moneydance:
   - this is not too much of an issue. You have to be aware of any 'oddities' and handle them a different way.
   - Java Extension:   Extension Container -> Java Extension Class(and its methods)
   - Python Extension: Extension Container(Py) -> Python Interpreter Instance(PyII) -> Py Extension(and its methods).

- To create/build an extension. The process is roughly as follows:
    - Download/install the development kit and read the notes: https://infinitekind.com/developer
    - At lot of the notes relate to java, but some are still valid.
    - You will need ANT and also to run "ant genkeys" (before you start) in the src directory (to create your own key-pair)

    - You will also need to create an mxt (zip) build script (or use ANT)

    - Essentially, you need to build the extension_name.mxt file. This is a zip file.
    - the mxt contains your *.py file(s) and script_info.dict at root level, and then..:
    - meta_info.dict in a sub directory structure called ./com/moneydance/modules/features/extension_name/

    - When you build/sign the mxt you will need the mxt file you just created and these files...:
    - extadmin.jar, moneydance-dev.jar, priv_key, pub_key. Then execute this command:
    - java -cp extadmin.jar:moneydance-dev.jar com.moneydance.admin.KeyAdmin signextjar priv_key private_key_id "extension_name" "extension_name.mxt"
    - If it worked, you will have a new file called s-extension_name.mxt.
    - If you want it 'signed' by IK, then you will have to submit it for review and signing. However, you can just run your mxt 'unsigned'

- There are several types of Py extensions:
   1) The 'true' Py run-time extension >> you need the following minimum (example) construct:

   class MyExtensionClass():
      def __init__(self):
          # Set up your variables here
      def initialize(self, extension_context, extension_object):
          self.moneydanceContext = extension_context
          self.moneydanceExtensionObject = extension_object
          self.moneydanceContext.registerFeature(extension_object, "uri:string:youwanttosend", [icon or None], "your_extension_id_name")
      def invoke(self, uri):
          print("Python extension received invoke command: %s" % (uri))
      def handle_event(self, eventString):
          print("Python extension received handle_event: %s" % (eventString))
      def unload(self):
          print("unload actions here")
      >> also define; __init__(), __str__(), getName(), handleEvent() [or handle_event()], unload() # the latter three are called since build 3056....
   moneydance_extension = MyExtensionClass()

   - script_info.dict needs to contain the "type"="initializer" and that's it!

   2) The 'script' method Py extension >> you need the following minimum construct:
      - Your main script. Decide when to run it (run time using initializer, or more normally via the extensions menu click action)
      - invoke.py, unload.py, handle_event.py, initializer.py scripts [all optional]
      - I suggest you use unload.py to cleanup on uninstall or reinstall
      - script_info.dict needs to contain a mixture of "type"="menu", "type"="method", "type"="initializer" options

>> AT THIS POINT, REVIEW THIS extension_tester example and the files within....

- So the extension types available to you:
  a) Your Py script simply contains an extn Class that you have defined and set the variable moneydance_extension = ExtensionClass()
     You run this script from Moneybot and then you will be asked if you want to install this extn. This lives until MD restart.
     >> I don't personally see this type of extension as being of any 'real' use other than prototyping and playing etc <<
  b) Script 'method': You create an .mxt bundle that contains script_info.dict with the key: "type" = "menu". When you install this then
     at MD launch a PyII is created and this is registered as an Extension and each "menu" item appears on the extensions menu (normally one only)
     When you select this menu item, MD basically just runs your Py script. So it's a quick and easy way to allow a user to run your
     script when they want. Technically, PyII will always exist in memory, and also everything your py script does after its executed will also
     remain in memory (and objects and JFrames for example will still be live), including its namespace. When you re-run the script/menu item
     then you get back into the same namespace from where you last left off. You need to handle this. Toolbox is an example of this.
     By default, this type of Py extension receives no extra method calls from Moneydance...
     - However, if you also define {"type" = "method", "method" = "x", "script_file" = "x.py"} entries in script_info.dict then
     - your extension can execute invoke, handle_event, unload Py scripts
     - This type of extension can also define an 'initializer' script,  but probably not needed
  c) ExtensionClass(): You create an .mxt bundle (similar to option b above, using the ExtensionClass(). This also uses script_info.dict, but this time the
     file should just contain a {"type" = "initializer", "script_file" = "extension_tester.py"} entry - you need nothing else.
     Assuming you define the ExtensionClass() and then use moneydance_extension = MyExtensionClass() then it will install itself.
     If you also use context.registerFeature() then it will appear on the extensions menu too. If the menu item is clicked, then it will call .invoke() method.
     You can also use moneydance.showURL() to call invoke.

- It's possible from here to create a HomePageView (Summary screen/dashboard 'widget'). These DO operate 'properly'!
     Within your Py script, as well as creating the ExtensionClass(), also create one for the HomePageView:
     class MyHomePageView(HomePageView) - It needs to contain the following methods:
     __init__(), getID(), toString(),__str__(), getGUIView(, book), setActive(, active), refresh(), reset()
     >> .getGUIView() must return a valid swing JComponent. This is what is displayed - e.g. return JTextField("Hello World")
     to register, at the same time as you call .registerFeature(), you can then call:
     self.moneydanceContext.registerHomePageView(extension_object, MyHomePageView()).
     NOTE: Use the extension_object as the first parameter, NOT your own extension class. Then MD will then be able to unload your widget
     whenever your extension is unloaded.
     >> It will take some investigation to get your HomePageView working properly, but then that's the fun of this...!

- If the User or MD uninstalls / reinstalls your extension, then .unload() method will be called, or the unload.py script, depending
     on how you defined it. Please utilise this to 'clean up' before your extension is 'killed'.. E.g. delete all references to data objects

- You might get to a point where you want to access a running Py Extension from elsewhere... There are several ways:
      - The easiest I have found is to extend the JFrame class and add some variables/references to your objects.
        You can use JFrame.getFrames() and then iterate to find yours, From there access the variables/references you defined
      - You can also use MD APIs to iterate installed extensions, and go from there...
      - There are also some more 'advanced' (sneaky) ways to do this, but out of the scope of this little jump-start document ;->

ACCESSING MONEYDANCE OBJECTS
- The 'moneydance' variable is your friend. It exists when your script is executed and is deleted once the script exits
    - This reference will never change and is constant
    - If using the script method extension then you should grab a reference - e.g. MD_REF = moneydance
    - You will need this if for example you use Swing JFrame() that is running after your script exits (it needs a reference back to 'moneydance')'.

- If using the ExtensionClass() method, your initialize() method will be called with the parameters context and extension_wrapper
    - you should save a reference to this using self.ext_context = context (thus this is the same as the moneydance object)

- There also exists a moneydance_ui variable. This can be None or set to the UI class.
    - You can save this using MD_REF_UI = moneydance_ui
    - If using the ExtensionClass(), then a better way is MD_REF_UI = MD_REF.getUI()
        - But be aware that .getUI() will try to load the UI if it's not loaded... You should await the "md:file:opened" event

- There also exists the moneydance_data variable. I advise against using this or storing a reference to it.
    - You MUST release any references to this when the dataset changes.
    - Best to just use MD_REF.getCurrentAccountBook() as this is the same as moneydance_data

>> Again, note that moneydance, moneydance_ui, moneydance_data get deleted when your script exits

- You can use moneydance_extension_loader.getResourceAsStream() to access files within your extension's mxt file (as of build 3056)


SWING
- You have full access to javax swing components - do your own research ;->

- For large scripts, especially  with Swing GUI components you should take care to run all GUI updates on the Swing Event Dispatch Thread (EDT)
  ... and 'heavy' non-GUI code off the EDT.
  - Moneybot scripts run off the EDT.
  - MXT type="menu" extensions/scripts (i.e. run via script_info: "type" = "menu") run ON the EDT (as you have to be in the MD GUI to click the menu).
  - ExtensionClass() runtime extensions will start OFF the EDT (as they trigger before the UI is loaded). (Unless you are installing, in which case it will be on the EDT then)
  - handle_events and invokes may be on or off the EDT
  - Extensions can also register themselves as listeners to various data model objects and those can definitely be called off the main thread,
        ... for example when objects are updated from the sync layer.

  >> Best bet is to test - e.g. 'if SwingUtilities.isEventDispatchThread(): then x'
     - You can use SwingUtilities.invokeLater() and SwingUtilities.invokeAndWait() as appropriate.
     - You can use SwingWorker to run 'heavy' non-GUI code off the EDT

  >> If you are a beginner writing tiny code, don't worry about the EDT. BUT if you are writing 'heavy' code, and or extensions
     for others, then research these matters ('Swing is not thread-safe') and take appropriate action(s) in your code.

CODING TIPS
- You access Moneydance via the published API: https://infinitekind.com/dev/apidoc/index.html - so start here.
- You can also access all Moneydance's internal code/classes. Best bet is to stick with the API.
- As it's Java, most standard stuff works first-time cross-platform. But not always... Test on Mac, Windows, Linux
- I recommend you install a free IDE. IntelliJ IDEA works well and has Python support. Without this you will find code editing difficult
    to set it up, create Project with Python 2.7 as the SDK, add a moneydance.jar as a Library,
    add a Java Module called Moneydance (link the Library, and assign the SDK adopt-openjdk-15 (Hotspot)).
    This will then give you a great code editor and inbuilt checking of your work....
- com.moneydance.util.Platform .isWindows() .isMac() [or .isOSX()] .isBigSurOrLater() .isUnix() are  very  useful methods.
- Don't use file extension filters with Mac and JFileChooser() - these will randomly hang your machine.
- Use FileDialog() on Windows to allow file creation. As when creating files with JFileChooser() on some machines, in some folder it can fail with a permission error
- Be aware of encoding issues. Moneydance uses UTF-8 as it's default (which is good), but Python 2.7 uses ASCII (which is not good):
    - This is not good practice, but do this 'hack' at the beginning of your code to get Python 2.7 to default to UTF-8
        import sys; reload(sys); sys.setdefaultencoding('utf8')
    - AVOID using str(). For example just use %s in text. So "Hello %s" %(name) - and not "Hello " + str(name)
    - If you use str(), especially anywhere where there are extended characters - like £ or € - you will either get garbage or an error.....
    The reference __file__ will not exist if running as an ExtensionClass()
- Account Filter  is very useful: com.infinitekind.moneydance.model.AcctFilter. It took me ages to work out.... - Example:
    class MyAcctFilter(AcctFilter):
        def matches(self, acct):
            if acct.getAccountType() == Account.AccountType.BANK
                return True
            return False
    accts = AccountUtil.allMatchesForSearch(moneydance_data, MyAcctFilter())
- Object listeners (API):
    AccountListener, BudgetListener, CurrencyListener, MDFileListener, MemorizedItemListener, OnlineInfoListener
    OnlinePayeeListener, OnlinePaymentListener, OnlineTxnListener, ReminderListener, TransactionListener

- Review:
    - Stuart Beesley's scripts (especially net_account_balances extension): https://yogi1967.github.io/MoneydancePythonScripts/
    - Mike Bray's excellent wiki:   https://bitbucket.org/mikerb/moneydance-2019/wiki/Moneydance%20Information
    - Virantha Ekanayake's tips: https://virantha.com/2016/11/28/moneydance-python-extension-tips/
                                 (ignore the elements in Virantha's tips about using java to package the extension)

- ExtensionClass():
    - __init__():     Perform simple variable initialisation here.
    - initialize():   Grab 'context' and 'extension wrapper' here. Context is your gateway into Moneydance. Perform simple startup tasks
                      but, remember, you need to be thinking 'event' driven, and not sequentially programmed driven.
                      at this point, during MD startup, the GUI is not loaded, the dataset is not loaded, and MD is firing up.....
                      (unless during a install/reinstall, as you will always be in the GUI then of course)
                      here you can call .registerFeature() [optional] to stick an item on the extensions menu
                      here you can call .registerHomePageView() [optional] if your extension will build a HomePage view too
    - invoke():       Will be called if you click on your [optional] extensions menu item; or via .showURL()
                      importantly, your own extension can call this during execution to trigger your own events...
    - handle_event(): Very important that you monitor MD events. The full list is at the end of this readme
                      'md:file:opened' is your trigger that MD, the GUI, the dataset is loaded - or when a dataset has changed
                      'md:file:closing' and 'closed' are good points to release all references to data objects
    - unload():       This is your trigger that your extension is being uninstalled or reinstalled. It needs to cleanup, release references, shutdown
    - other...        Use float(context.getBuild()) to check MD build and handle version control / compatibility accordingly
                      always consider what thread you are on (Swing EDT or not) and handle accordingly
                      to write to the MD console: 'from java.lang import System' and then 'System.err.write("text\n")'
                      there are some prebuilt popups you can use in .getUI() .askQuestion() .askForInput() .showInfoMessage()
                      your extension probably needs a GUI... Swing JFrame() etc is the way to go. DO NOT instantiate
                      .. your Swing until after the UI and the Dataset are loaded ('strange' things will happen)
    - advanced...     You don't have Java Synchronized.. If you need this, consider self.lock = threading.Lock() and then 'with self.lock: ...'
                      do not update the Look and Feel (LAF). Override .updateUI() in JComponents and super(YourClass, self).updateUI()

- Moneydance data:    Read the API. Look at others' scripts. Learn the model. It's confusing at first, but becomes clear(er) over time.
                      review Stuart Beesley's scripts: https://yogi1967.github.io/MoneydancePythonScripts/
                      this is a very good 'primer': https://bitbucket.org/mikerb/moneydance-2019/wiki/Moneydance%20Information

There are also more 'advanced' ways to access and manage your Py Extension but try to keep everything MD friendly and to survive upgrades.
Details of these are out of scope for this document, I will  be happy to discuss / brainstorm these with anyone who wants
to contact me about them....


KEY FILES YOU NEED TO CREATE

script_info.dict: Locate in the root of your .mxt file
{
  "actions" = (
    {
      "type" = "initializer"                    # [optional]
      "script_file" = "initializer_script.py"
    }
    {
      "type" = "menu"                           # [optional] - Can have multiple entries
      "script_file" = "menu_script.py"
      "name" = "Extension Name"                 # This is the name of the extensions menu item
    }
    {
      "type" = "method"                         # [optional] - can be invoke, handle_event, unload. Can have multiple entries
      "method" = "the_method"
      "script_file" = "the_method.py"
    }  )
}

meta_info.dict: Locate in the ./com/moneydance/modules/features/extension_name/ directory of your .mxt file
{
  "id" = "extension_name"                       # All lowercase. This is your Extension's identity to Moneydance
  "extension_type" = "python"                   # Always python
  "vendor" = "The Infinite Kind"                # This is you
  "module_build" = "1"                          # Your build/version
  "minbuild" = "3056"                           # The minimum MD build for this extension
  "maxbuild" = "999"                            # Optional, not normally used. Max version of MD to run extension on.
  "vendor_url" = "https://infinitekind.com"     # Your own url
  "module_name" = "Extension Tester"            # User friendly extension name
  "module_desc" = "extension description"       # Long description
  "mac_sandbox_friendly" = "true"               # Optional
}


Moneydance Events:

# These are the MD events...
# md:file:opened is the key one when the dataset and the GUI are loaded.

# You should release any reference to MD data objects if dataset is closed/opened!

# md:file:closing	The Moneydance file is being closed
# md:file:closed	The Moneydance file has closed
# md:file:opening	The Moneydance file is being opened
# md:file:opened	The Moneydance file has opened
# md:file:presave	The Moneydance file is about to be saved
# md:file:postsave	The Moneydance file has been saved
# md:app:exiting	Moneydance is shutting down
# md:account:select	An account has been selected by the user
# md:account:root	The root account has been selected
# md:graphreport	An embedded graph or report has been selected
# md:viewbudget	    One of the budgets has been selected
# md:viewreminders	One of the reminders has been selected
# md:licenseupdated	The user has updated the license


Thanks for reading.. Contact me with questions, updates... Happy Python coding.... Stuart Beesley
Last updated: 7th April 2021

