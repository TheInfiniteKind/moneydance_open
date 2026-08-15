package com.moneydance.modules.features.contextmenutools

import com.infinitekind.moneydance.model.AbstractTxn
import com.infinitekind.moneydance.model.Account
import com.infinitekind.moneydance.model.CurrencyType
import com.infinitekind.util.AppDebug
import com.infinitekind.util.StreamTable
import com.infinitekind.util.labelify
import com.moneydance.apps.md.controller.*
import com.moneydance.apps.md.view.gui.*
import com.moneydance.awt.GridC
import com.moneydance.modules.features.contextmenutools.util.TextViewerDialog
import com.moneydance.modules.features.contextmenutools.util.Util
import com.moneydance.modules.features.contextmenutools.util.Util.logConsole
import java.awt.BorderLayout
import java.awt.GridBagLayout
import javax.swing.*
import javax.swing.border.EmptyBorder

@Suppress("DuplicatedCode")

interface ContextMenuAction {
  fun getActions(menuContext:MDActionContext, listAccts:List<Account>, listTxns:List<AbstractTxn>):List<Action>
}

/**
 * A collection of context menu (right click) tools that hook into Moneydance's context menu...
 *
 * @author Stuart Beesley - March 2026
 * @since MD2024.4(5253)
 */
class Main : FeatureModule(), PreferencesListener {
  
  override fun init() {
    EXTN_ID = moduleID
    
    val context = context
    mdMain = context as com.moneydance.apps.md.controller.Main  // upcast back to main to get full Moneydance capabilites
    val mdMain = mdMain!! // shadow copy and null-check once/upfront
    
    Util.APPDEBUG_ENABLED = mdMain.build >= 5100
    require(mdMain.build >= 5253) { "Sorry, this extension is only enabled for MD2024.4(5253) onwards...." }

    // if moneydance was launched with -d or the system property is set.....
    DEBUG = (com.moneydance.apps.md.controller.Main.DEBUG || java.lang.Boolean.getBoolean("moneydance.debug"))
    logConsole(true, "** DEBUG IS ON **")
    
    extensionContext = this
    
    addPreferencesListener()
    
    //register on the extensions menu
    context.registerFeature(this, moduleID, null, getName())
    logConsole("Initialized (Kotlin) build: $versionString ${if (PREVIEW_BUILD) "(PREVIEW) " else ""}")

    nukeLegacyPrefKeys()
  }
  
  /**
   * Return a list of contextual actions (javax.swing.Action) that the extension can perform
   * on target objects which are given in the context parameter, along with references to the kind of context and the UI object.
   * The default implementation of this method returns an empty list. If you override it,
   * please ensure that it returns quickly so that the context menu appearance remains snappy.
   *
   * @param context Information about the context, including
   * @return a list of actions that the UI can perform on the
   *
   * @since Moneydance 2024 (build 5100)
   */
  override fun getActionsForContext(context:MDActionContext):List<Action> {

    val actions = mutableListOf<Action>()

    val listAccts = context.accounts
    val listTxns = context.items.filterIsInstance<AbstractTxn>()
    
    val prefs = mdMain?.preferences ?: return actions
    val menuSettings = prefs.getTableSetting(EXTN_ID + SETTING_MASTER_KEY, null) ?: StreamTable()
    val dupMenuEnabled = getMenuBoolSetting(menuSettings, SETTING_MENU_DUP_ENABLED, true)
    val vstMenuEnabled = getMenuBoolSetting(menuSettings, SETTING_MENU_VST_ENABLED, true)
    val jumpMenuEnabled = getMenuBoolSetting(menuSettings, SETTING_MENU_JUMP_ENABLED, true)
    val copyPasteMenuEnabled = getMenuBoolSetting(menuSettings, SETTING_MENU_COPYPASTE_ENABLED, true)
    val templateMenuEnabled = getMenuBoolSetting(menuSettings, SETTING_MENU_TEMPLATE_ENABLED, true)
    val rebalanceMenuEnabled = getMenuBoolSetting(menuSettings, SETTING_MENU_REBALANCE_ENABLED, true)
    val templateIncludeSingleSplit = getMenuBoolSetting(menuSettings, SETTING_TEMPLATE_INCLUDE_SINGLE_SPLIT, false)
    val templateNameFilter = getMenuStringSetting(menuSettings, SETTING_TEMPLATE_NAME_FILTER, "")
    val templateMatchAccount = getMenuBoolSetting(menuSettings, SETTING_TEMPLATE_MATCH_ACCOUNT, false)
    val excludeExpiredReminders = getMenuBoolSetting(menuSettings, SETTING_TEMPLATE_EXCLUDE_EXPIRED, false)
    val copyRawMenuEnabled = getMenuBoolSetting(menuSettings, SETTING_MENU_COPY_RAW_ENABLED, false)
    val showRawMenuEnabled = getMenuBoolSetting(menuSettings, SETTING_MENU_SHOW_RAW_ENABLED, false)
    val alwaysConfirmTotal = getMenuBoolSetting(menuSettings, SETTING_ALWAYS_CONFIRM_TOTAL, false)
    
    if (debugMenuEnabled || DEBUG) {
      val summary = "ContextMenuTools: type=${context.type.name} dateRange=${context.dateRange} " +
                    "accts=${listAccts.size} txns=${listTxns.size} items=${context.items.size} " +
                    "obj=${context.contextObject?.let { "${it::class.qualifiedName} ${if (it is Account) (it.getAccountType().toString() + " " + it.fullAccountName) else it}" }}"
      
      if (DEBUG) {
        AppDebug.ALL.log {
          ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n" +
          "ContextMenuTools#getActionsForContext >>\n" +
          "type:      ${context.type.let { "${it::class.simpleName}.${it.name}" }}\n" +
          "obj:       ${context.contextObject?.let { "${it::class.qualifiedName} ${if (it is Account) (it.getAccountType().toString() + " " + it.fullAccountName) else it}" }}\n" +
          "comp:      ${context.component?.let { "${it::class.qualifiedName} $it" }}\n" +
          "dateRange: ${context.dateRange}\n" +
          "accts:     ${listAccts.let { "${it.size} $it" }}\n" +
          "txns:      ${listTxns.let { "${it.size} $it" }}\n" +
          "items:     ${context.items.let { "${it.size} $it" }}\n" +
          ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        }
      } else {
        Util.logConsole(summary)
      }
    }

    // Copy Raw Details to Clipboard: no context-type or account-type restriction whatsoever -
    // applies wherever any txns are received, so it's wired unconditionally, before the
    // quick-exit check below (which only bails when BOTH txns and accts are empty).
    actions += CopyRawDetailsToClipboard(copyEnabled = copyRawMenuEnabled, showEnabled = showRawMenuEnabled)
      .getActions(menuContext = context, listAccts = listAccts, listTxns = listTxns)
    
    // quick do-nothing exit if there are no items/accounts to process...
    if (listTxns.isEmpty() && listAccts.isEmpty()) return actions
    
    if (isDataEntryRegisterActionType(contextType = context.type, includeSecReg = true) || isSearchActionType(contextType = context.type)) {
      if (vstMenuEnabled) actions += ValueSelectedTxns().getActions(menuContext = context, listAccts = listAccts, listTxns = listTxns)
    }
    
    if (isDataEntryRegisterActionType(contextType = context.type, includeSecReg = false)) {
      if (dupMenuEnabled) actions += DuplicateTransactions().getActions(menuContext = context, listAccts = listAccts, listTxns = listTxns)
      actions += CopyPasteSplits(
        copyPasteEnabled = copyPasteMenuEnabled,
        templateEnabled = templateMenuEnabled,
        includeSingleSplitReminders = templateIncludeSingleSplit,
        templateNameFilter = templateNameFilter,
        templateMatchAccount = templateMatchAccount,
        excludeExpiredReminders = excludeExpiredReminders,
        rebalanceEnabled = rebalanceMenuEnabled,
        alwaysConfirmTotal = alwaysConfirmTotal
      ).getActions(menuContext = context, listAccts = listAccts, listTxns = listTxns)
    }
    
    if (isDataEntryRegisterActionType(contextType = context.type, includeSecReg = false) || isSearchActionType(contextType = context.type)) {
      if (jumpMenuEnabled) actions += JumpToDate().getActions(menuContext = context, listAccts = listAccts, listTxns = listTxns)
    }
    
    return actions
  }
  
  private fun isSearchActionType(contextType:ActionContextType):Boolean =
    contextType == ActionContextType.home_search || contextType == advancedSearchType
  
  private fun isDataEntryRegisterActionType(contextType:ActionContextType, includeSecReg:Boolean):Boolean =
    contextType in buildSet {
      add(ActionContextType.register)
      add(ActionContextType.invest_register)
      add(ActionContextType.loan_register)
      if (includeSecReg) add(ActionContextType.security_register)
    }
  
  override fun cleanup() {
    // never actually called by Moneydance!?
    logConsole(true, "::cleanup() called (will pass onto .unload()....)...")
    unload()
  }
  
  override fun unload() {
    // NOTE: we are using SecondaryWindow/Dialog(s), and they should auto-close/cleanup when dataset changes....
    logConsole(true, "::unload() called....")
    removePreferencesListener()

    @Suppress("UsePropertyAccessSyntax")
    val secWindows = mdGUI.getSecondaryWindows().toList()

    try {
      secWindows.forEach { win ->
        if (win is SecondaryFrame) {
          if (win.name.equals(moduleID, ignoreCase = true)) {
            logConsole(true, "... attempting to close: '${win.javaClass.simpleName}'")
            win.goAway()
          }
        } else if (win is SecondaryDialog) {
          if (win.name.equals(moduleID, ignoreCase = true)) {
            logConsole(true, "... attempting to close: '${win.javaClass.simpleName}'")
            win.goAway()
          }
        }
      }
    } catch (e: Exception) { logConsole("Error closing window: '$e'") }
  }
  
  override fun handleEvent(appEvent:String) {
    logConsole(true, "::handleEvent($appEvent)")
    when {
      appEvent.equals(AppEventManager.FILE_OPENED, ignoreCase = true) -> copiedSplits = null
       appEvent.equals(AppEventManager.FILE_OPENING, ignoreCase = true) -> copiedSplits = null
       appEvent.equals(AppEventManager.FILE_CLOSING, ignoreCase = true) -> copiedSplits = null
       appEvent.equals(AppEventManager.FILE_CLOSED, ignoreCase = true) -> copiedSplits = null
    }

    // on ANY event, expire a stale copy regardless of event type (instead of a timer)
    copiedSplits?.let { copy ->
      if (System.currentTimeMillis() - copy.copiedAtMillis > CopyPasteSplits.COPY_EXPIRY_MILLIS) {
        copiedSplits = null
        if (debugMenuEnabled || DEBUG) logConsole("CopyPasteSplits: cleared stale copy (>10min) on '$appEvent'")
      }
    }
  }
  
  /** Process an invocation of this module with the given URI  */
  override fun invoke(uri: String) {
    var command = uri
    val params: String
    val colonIdx = uri.indexOf(':')
    if (colonIdx >= 0) {
      command = uri.substring(0, colonIdx)
      params = uri.substring(colonIdx + 1)
    } else {
      params = ""
    }
    logConsole(true, "::invoke($uri) - command: '$command' params: $params")

    when (command) {
      moduleID -> showConfigDialog()
      else -> logConsole("::invoke($uri) - no valid id/command received >> doing nothing")
    }
  }
  
  private fun showConfigDialog() {
    val dlg = MenuConfigDialog()
    dlg.setName(moduleID)
    dlg.isVisible = true
  }
  
  private class MenuConfigDialog:SecondaryDialog(mdGUI, null, STRING_CONFIG, false), OKButtonListener {
    
    private val menuSettingsOnOpen = prefs.getTableSetting(EXTN_ID + SETTING_MASTER_KEY, null) ?: StreamTable()
    
    private val enableMenuDupCheckbox = JCheckBox(STRING_MENU_DUP_ENABLED).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_MENU_DUP_ENABLED, true)
    }
    
    private val enableMenuVSTCheckbox = JCheckBox(STRING_MENU_VST_ENABLED).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_MENU_VST_ENABLED, true)
    }
    
    private val enableMenuJumpCheckbox = JCheckBox(STRING_MENU_JUMP_ENABLED).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_MENU_JUMP_ENABLED, true)
    }
    
    private val enableMenuCopyPasteCheckbox = JCheckBox(STRING_MENU_COPYPASTE_ENABLED).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_MENU_COPYPASTE_ENABLED, true)
    }
    
    private val enableMenuTemplateCheckbox = JCheckBox(STRING_MENU_TEMPLATE_ENABLED).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_MENU_TEMPLATE_ENABLED, true)
    }
    
    private val enableMenuRebalanceCheckbox = JCheckBox(STRING_MENU_REBALANCE_ENABLED).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_MENU_REBALANCE_ENABLED, true)
    }
    
    private val includeSingleSplitCheckbox = JCheckBox(STRING_TEMPLATE_INCLUDE_SINGLE_SPLIT).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_TEMPLATE_INCLUDE_SINGLE_SPLIT, false)
      isEnabled = enableMenuTemplateCheckbox.isSelected
    }
    
    private val templateMatchAccountCheckbox = JCheckBox(STRING_TEMPLATE_MATCH_ACCOUNT).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_TEMPLATE_MATCH_ACCOUNT, false)
      isEnabled = enableMenuTemplateCheckbox.isSelected
    }
    
    private val excludeExpiredRemindersCheckbox = JCheckBox(STRING_TEMPLATE_EXCLUDE_EXPIRED).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_TEMPLATE_EXCLUDE_EXPIRED, false)
      isEnabled = enableMenuTemplateCheckbox.isSelected
    }
    
    private val templateNameFilterField = JTextField(getMenuStringSetting(menuSettingsOnOpen, SETTING_TEMPLATE_NAME_FILTER, ""), 20).apply {
      isEnabled = enableMenuTemplateCheckbox.isSelected
    }
    
    private val alwaysConfirmTotalCheckbox = JCheckBox(STRING_ALWAYS_CONFIRM_TOTAL).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_ALWAYS_CONFIRM_TOTAL, false)
      isEnabled = enableMenuCopyPasteCheckbox.isSelected || enableMenuTemplateCheckbox.isSelected
    }
    
    private val hamiltonLinkLabel = JLabel(STRING_HAMILTON_LINK_TEXT).apply {
      foreground = Util.blue
      cursor = java.awt.Cursor(java.awt.Cursor.HAND_CURSOR)
      toolTipText = STRING_HAMILTON_LINK_TOOLTIP
      addMouseListener(object:java.awt.event.MouseAdapter() {
        override fun mouseClicked(e:java.awt.event.MouseEvent) {
          mdGUI.showInternetURL(HAMILTON_WIKI_URL)
        }
      })
    }
    
    private val helpInfoButton = JButton(STRING_INFO_BUTTON).apply {
      addActionListener {
        val readmeText = Util.loadTextResource("readme.txt")
        val win = TextViewerDialog(
          mdGUI, this@MenuConfigDialog, STRING_HELP_INFO_TITLE, readmeText, STRING_COPY_TO_CLIPBOARD,
          sizeKey = "$EXTN_ID.gui.help_info.size",
          locationKey = "$EXTN_ID.gui.help_info.loc"
        )
        win.isVisible = true
      }
    }
    
    private val enableMenuCopyRawCheckbox = JCheckBox(STRING_MENU_COPY_RAW_ENABLED).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_MENU_COPY_RAW_ENABLED, false)
    }
    
    private val enableMenuShowRawCheckbox = JCheckBox(STRING_MENU_SHOW_RAW_ENABLED).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_MENU_SHOW_RAW_ENABLED, false)
    }
    
    private val enableMenuDebugCheckbox = JCheckBox(STRING_DEBUG_ENABLED).apply {
      isSelected = getMenuBoolSetting(menuSettingsOnOpen, SETTING_MENU_DEBUG_ENABLED, false)
    }
    
    private val vstBaseCurrLabel = JLabel(STRING_MENU_VST_DISP_CURR.labelify)
    
    var currencyModel:CurrencyModel? = null
    var vstBaseCurrChoice:JComboBox<CurrencyType>? = null
    
    init {
      this.name = EXTN_ID
      
      val book = mdMain?.currentAccountBook
      book!!
      val ctable = book.currencies

      currencyModel = CurrencyModel(book.currencies, CurrencyType.Type.CURRENCY)
      vstBaseCurrChoice = JComboBox(currencyModel).also { it.isEnabled = enableMenuVSTCheckbox.isSelected}
      
      enableMenuVSTCheckbox.addActionListener { vstBaseCurrChoice!!.isEnabled = enableMenuVSTCheckbox.isSelected }

      enableMenuTemplateCheckbox.addActionListener {
        includeSingleSplitCheckbox.isEnabled = enableMenuTemplateCheckbox.isSelected
        templateMatchAccountCheckbox.isEnabled = enableMenuTemplateCheckbox.isSelected
        excludeExpiredRemindersCheckbox.isEnabled = enableMenuTemplateCheckbox.isSelected
        templateNameFilterField.isEnabled = enableMenuTemplateCheckbox.isSelected
        alwaysConfirmTotalCheckbox.isEnabled = enableMenuCopyPasteCheckbox.isSelected || enableMenuTemplateCheckbox.isSelected
      }
      
      enableMenuCopyPasteCheckbox.addActionListener {
        alwaysConfirmTotalCheckbox.isEnabled = enableMenuCopyPasteCheckbox.isSelected || enableMenuTemplateCheckbox.isSelected
      }
      
      val ct = vstBaseCurrChoice?.selectedItem as? CurrencyType ?: book.currencies.baseType
      val currIdString = prefs.getSetting(UserPreferences.GUI_POPUP_USER_CURR_ID_OVERRIDE, ct.idString)
      ctable.getCurrencyByIDString(currIdString)?.let { vstBaseCurrChoice?.selectedItem = it }
      
      layout = BorderLayout()
      
      val form = JPanel(GridBagLayout())
      form.border = EmptyBorder(16, 20, 12, 20)
      var y = 0
      
      form.add(JSeparator(), GridC.getc(0, y++).west().wx(1f).fillboth().insets(6, 0, 6, 0))

      form.add(enableMenuShowRawCheckbox, GridC.getc(0, y++).west().insets(4, 4, 4, 4))
      form.add(enableMenuCopyRawCheckbox, GridC.getc(0, y++).west().insets(4, 4, 4, 4))
      
      form.add(JSeparator(), GridC.getc(0, y++).west().wx(1f).fillboth().insets(6, 0, 6, 0))
      
      form.add(enableMenuVSTCheckbox, GridC.getc(0, y++).west().insets(4, 4, 2, 4))
      
      val currPanel = JPanel(GridBagLayout())
      currPanel.add(vstBaseCurrLabel, GridC.getc(0, 0).west().insets(0, 0, 0, 6))
      currPanel.add(vstBaseCurrChoice!!, GridC.getc(1, 0).west().insets(0, 0, 0, 0))
      
      form.add(currPanel, GridC.getc(0, y++).west().insets(0, 24, 4, 4))
      
      form.add(JSeparator(), GridC.getc(0, y++).west().wx(1f).fillboth().insets(6, 0, 6, 0))
      
      form.add(enableMenuDupCheckbox, GridC.getc(0, y++).west().insets(4, 4, 4, 4))

      form.add(JSeparator(), GridC.getc(0, y++).west().wx(1f).fillboth().insets(6, 0, 6, 0))

      form.add(enableMenuCopyPasteCheckbox, GridC.getc(0, y++).west().insets(4, 4, 4, 4))
      form.add(enableMenuTemplateCheckbox, GridC.getc(0, y++).west().insets(4, 4, 4, 4))
      form.add(includeSingleSplitCheckbox, GridC.getc(0, y++).west().insets(0, 24, 4, 4))
      form.add(templateMatchAccountCheckbox, GridC.getc(0, y++).west().insets(0, 24, 4, 4))
      form.add(excludeExpiredRemindersCheckbox, GridC.getc(0, y++).west().insets(0, 24, 4, 4))
      
      val templateFilterPanel = JPanel(GridBagLayout())
      templateFilterPanel.add(JLabel(STRING_TEMPLATE_NAME_FILTER.labelify), GridC.getc(0, 0).west().insets(0, 0, 0, 6))
      templateFilterPanel.add(templateNameFilterField, GridC.getc(1, 0).west().insets(0, 0, 0, 0))
      form.add(templateFilterPanel, GridC.getc(0, y++).west().insets(0, 24, 4, 4))
      
      form.add(enableMenuRebalanceCheckbox, GridC.getc(0, y++).west().insets(4, 4, 4, 4))
      
      form.add(alwaysConfirmTotalCheckbox, GridC.getc(0, y++).west().insets(0, 24, 4, 4))
      
      form.add(JSeparator(), GridC.getc(0, y++).west().wx(1f).fillboth().insets(6, 0, 6, 0))
      
      form.add(enableMenuJumpCheckbox, GridC.getc(0, y++).west().insets(4, 4, 4, 4))
      
      form.add(JSeparator(), GridC.getc(0, y++).west().wx(1f).fillboth().insets(6, 0, 6, 0))
      
      form.add(enableMenuDebugCheckbox, GridC.getc(0, y++).west().insets(4, 4, 4, 4))
      
      form.add(JSeparator(), GridC.getc(0, y++).west().wx(1f).fillboth().insets(6, 0, 6, 0))

      form.add(hamiltonLinkLabel, GridC.getc(0, y++).west().insets(8, 4, 4, 4))
      
      add(form, BorderLayout.CENTER)
      val buttonPanel = JPanel(BorderLayout())
      buttonPanel.border = EmptyBorder(0, 20, 12, 12)
      buttonPanel.add(helpInfoButton, BorderLayout.WEST)
      buttonPanel.add(OKButtonPanel(mdGUI, this, OKButtonPanel.QUESTION_OK_CANCEL), BorderLayout.CENTER)
      add(buttonPanel, BorderLayout.SOUTH)
      
      setEscapeKeyCancels(true)
      pack()
      setLocationRelativeTo(null)
      isResizable = false
    }
    
    override fun goneAway() {
      currencyModel?.goneAway()
      currencyModel = null
      vstBaseCurrChoice = null
    }
    
    override fun buttonPressed(answer:Int) {
      when (answer) {
        OKButtonPanel.ANSWER_OK -> {
          
          val menuSettings = prefs.getTableSetting(EXTN_ID + SETTING_MASTER_KEY, null) ?: StreamTable()
          menuSettings[SETTING_MENU_DUP_ENABLED] = enableMenuDupCheckbox.isSelected
          menuSettings[SETTING_MENU_VST_ENABLED] = enableMenuVSTCheckbox.isSelected
          menuSettings[SETTING_MENU_JUMP_ENABLED] = enableMenuJumpCheckbox.isSelected
          menuSettings[SETTING_MENU_COPYPASTE_ENABLED] = enableMenuCopyPasteCheckbox.isSelected
          menuSettings[SETTING_MENU_TEMPLATE_ENABLED] = enableMenuTemplateCheckbox.isSelected
          menuSettings[SETTING_MENU_REBALANCE_ENABLED] = enableMenuRebalanceCheckbox.isSelected
          menuSettings[SETTING_MENU_DEBUG_ENABLED] = enableMenuDebugCheckbox.isSelected
          menuSettings[SETTING_TEMPLATE_INCLUDE_SINGLE_SPLIT] = includeSingleSplitCheckbox.isSelected
          menuSettings[SETTING_TEMPLATE_MATCH_ACCOUNT] = templateMatchAccountCheckbox.isSelected
          menuSettings[SETTING_TEMPLATE_EXCLUDE_EXPIRED] = excludeExpiredRemindersCheckbox.isSelected
          menuSettings[SETTING_TEMPLATE_NAME_FILTER] = templateNameFilterField.text.trim()
          menuSettings[SETTING_ALWAYS_CONFIRM_TOTAL] = alwaysConfirmTotalCheckbox.isSelected
          menuSettings[SETTING_MENU_COPY_RAW_ENABLED] = enableMenuCopyRawCheckbox.isSelected
          menuSettings[SETTING_MENU_SHOW_RAW_ENABLED] = enableMenuShowRawCheckbox.isSelected

          prefs.setSetting(EXTN_ID + SETTING_MASTER_KEY, menuSettings)
          
          val book = mdMain?.currentAccountBook
          val base = mdMain?.currentAccountBook?.currencies?.baseType
          val currencies = mdMain?.currentAccountBook?.currencies

          book!!
          base!!
          currencies!!
          
          prefs.setSetting(UserPreferences.GUI_POPUP_USER_CURR_ID_OVERRIDE, "")  // by default blank the field
          val newBaseCurr = vstBaseCurrChoice!!.selectedItem as? CurrencyType ?: book.currencies.baseType
          if (newBaseCurr.idString != base.idString) {
            prefs.setSetting(UserPreferences.GUI_POPUP_USER_CURR_ID_OVERRIDE, newBaseCurr.idString)
          }
          goAway()
        }
        OKButtonPanel.ANSWER_CANCEL -> { goAway() }
      }
    } //// end buttonPressed ////

  } //// end MenuConfigDialog ////
  
  override fun getName(): String { return getModuleMetaData().moduleName }
  private fun addPreferencesListener() { context?.let { mdMain?.preferences?.addListener(this) } }
  private fun removePreferencesListener() { context?.let { mdMain?.preferences?.removeListener(this) }
  
  }
  
  override fun preferencesUpdated() {
    logConsole(true, "::preferencesUpdated() called - doing nothing")
  }
  
  private fun nukeLegacyPrefKeys() {
    //TODO - eliminate this at some point
    val prefs = mdMain?.preferences ?: return
    listOf(
      SETTING_MENU_DUP_ENABLED,
      SETTING_MENU_VST_ENABLED,
      SETTING_MENU_JUMP_ENABLED,
      SETTING_MENU_COPYPASTE_ENABLED,
      SETTING_MENU_TEMPLATE_ENABLED,
      SETTING_MENU_DEBUG_ENABLED
    ).forEach { key ->
      prefs.setSetting("$EXTN_ID$key", null as String?)
      prefs.setSetting("$EXTN_ID.$key", null as String?)
    }
  }


  val debugMenuEnabled
    get():Boolean {
      val prefs = mdMain?.preferences ?: return false
      val menuSettings = prefs.getTableSetting(EXTN_ID + SETTING_MASTER_KEY, null) ?: return false
      return getMenuBoolSetting(menuSettings, SETTING_MENU_DEBUG_ENABLED, false)
    }
  
  companion object {

    @JvmField var mdMain:com.moneydance.apps.md.controller.Main? = null
    
    val unprotectedContext:FeatureModuleContext? get() = mdMain
    val mdGUI:MoneydanceGUI get() = mdMain?.ui!! as MoneydanceGUI
    val versionString:String get() = "${extensionContext?.build ?: "???"}"

    @JvmStatic var EXTN_ID = "???"
    
    @JvmStatic var DEBUG = false

    @JvmField var copiedSplits: CopyPasteSplits.CopiedSplitsSnapshot? = null
    
    var extensionContext:Main? = null
    var PREVIEW_BUILD = true            //TODO - update accordingly
    
    const val STRING_EXTN_MENU = "Context Menu Tools..."
    const val STRING_CONFIG = "Context Menu Tools: Configuration"

    const val STRING_MENU_DUP_ENABLED = "Enable context menu: 'Duplicate'"
    const val STRING_MENU_VST_ENABLED = "Enable context menu: 'Value Selected Transactions'"
    const val STRING_MENU_VST_DISP_CURR = "Display Currency"
    const val STRING_MENU_JUMP_ENABLED = "Enable context menu: 'Jump to date'"
    const val STRING_MENU_COPYPASTE_ENABLED = "Enable context menu: 'Copy/Paste Splits'"
    const val STRING_MENU_TEMPLATE_ENABLED = "Enable context menu: 'Apply Splits Template'"
    const val STRING_MENU_REBALANCE_ENABLED = "Enable context menu: 'Rebalance Splits'"
    const val STRING_TEMPLATE_INCLUDE_SINGLE_SPLIT = "Include single split reminders"
    const val STRING_TEMPLATE_MATCH_ACCOUNT = "Reminder account must match target account"
    const val STRING_TEMPLATE_EXCLUDE_EXPIRED = "Exclude expired/inactive reminders"
    const val STRING_TEMPLATE_NAME_FILTER = "Filter reminder list by name contains"
    const val STRING_MENU_COPY_RAW_ENABLED = "Enable context menu: 'Copy Raw Details to Clipboard'"
    const val STRING_MENU_SHOW_RAW_ENABLED = "Enable context menu: 'Show Raw Details'"
    const val STRING_ALWAYS_CONFIRM_TOTAL = "Always confirm total when pasting splits"
    const val STRING_DEBUG_ENABLED = "Enable debug messages"
    const val STRING_HAMILTON_LINK_TEXT = "About the largest-remainder (Hamilton's) allocation method"
    const val STRING_HAMILTON_LINK_TOOLTIP = "Opens the Wikipedia article in your browser"
    const val HAMILTON_WIKI_URL = "https://en.wikipedia.org/wiki/Largest_remainder_method"
    const val STRING_INFO_BUTTON = "Info"
    const val STRING_HELP_INFO_TITLE = "Context Menu Tools - Help / Info"
    const val STRING_COPY_TO_CLIPBOARD = "Copy to Clipboard"
    
    const val SETTING_MASTER_KEY = ".settings"
    const val SETTING_MENU_DUP_ENABLED = "menu.enabled.duplicate"
    const val SETTING_MENU_VST_ENABLED = "menu.enabled.valueseltxns"
    const val SETTING_MENU_JUMP_ENABLED = "menu.enabled.jump"
    const val SETTING_MENU_COPYPASTE_ENABLED = "menu.enabled.copypaste"
    const val SETTING_MENU_TEMPLATE_ENABLED = "menu.enabled.template"
    const val SETTING_MENU_REBALANCE_ENABLED = "menu.enabled.rebalance"
    const val SETTING_MENU_DEBUG_ENABLED = "menu.enabled.debug"
    const val SETTING_TEMPLATE_INCLUDE_SINGLE_SPLIT = "paste.template.include_single_split"
    const val SETTING_TEMPLATE_MATCH_ACCOUNT = "paste.template.match_account"
    const val SETTING_TEMPLATE_EXCLUDE_EXPIRED = "paste.template.exclude_expired"
    const val SETTING_TEMPLATE_NAME_FILTER = "paste.template.name_filter"
    const val SETTING_MENU_COPY_RAW_ENABLED = "menu.enabled.copyraw"
    const val SETTING_MENU_SHOW_RAW_ENABLED = "menu.enabled.showraw"
    const val SETTING_ALWAYS_CONFIRM_TOTAL = "paste.always_confirm_total"
    
    private fun getMenuBoolSetting(table:StreamTable, key:String, default:Boolean):Boolean = table.getBoolean(key, default)
    private fun getMenuStringSetting(table:StreamTable, key:String, default:String):String { return (table[key] as? String) ?: default }
    
    // advanced_search is new for MD2026(5500)
    internal val advancedSearchType:ActionContextType? by lazy {
      try { ActionContextType::class.java.getField("advanced_search").get(null) as ActionContextType
      } catch (_:NoSuchFieldException) { null }
    }
    
  } // end companion object
}