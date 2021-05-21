Author: Stuart Beesley - StuWareSoftSystems (March 2021 - a lockdown project)

Get more Scripts/Extensions from: https://yogi1967.github.io/MoneydancePythonScripts/

Extension format only >> Minimum Moneydance version 2021.1 (build: 3056, ideally 3069 onwards)
(If you have installed the extension, but nothing happens, then check your Moneydance version)

This is a Python(Jython 2.7) Extension that runs inside of Moneydance via the Moneybot Python Interpreter
It's a prototype to demonstrate the capabilities of Python. Yes - if you can do it in Java, you can do it in Python too!

DISCLAIMER: THIS EXTENSION IS READONLY - BUT YOU USE AT YOUR OWN RISK!

PURPOSE

This extension creates a Moneydance Home Page View >> a little widget on the Home / Summary Screen dashboard

- Drag and drop the .mxt file onto the left side bar to install (or use Extensions, Manage Extensions, add from file)
- Once installed, visit Preferences > Summary Page, and then move the new widget to the desired Home screen location

- This widget allows you to select multiple accounts. The balances are totalled to present on the Home screen widget
- My concept was to add balances to target zero. Thus a positive number is 'good', a negative is 'bad'
- The idea is that you net cash and debt to get back to zero every month
- However, you could create a Net Worth Balance for example; you can use it for anything really

- You can change the widget name and also the balance type in the config screen (click the widget, or extensions menu)
- Any non base currency accounts are converted back to your base currency
- NOTE: This does not use recursive balance totalling, it simply uses the selected accounts' balance...

Thanks for reading..... ;->