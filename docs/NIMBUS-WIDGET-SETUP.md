# Configure stock Nimbus for CP02 (safe, reversible)

**Start with Kodi working normally. Save screenshots of your existing Nimbus settings/widget sources before you change them.** Kodi skins and settings labels vary by version; if your Nimbus menus look different, stop rather than resetting Kodi or reinstalling the skin.

1. Install the CP02 ZIP through **Kodi → Settings → Add-ons → Install from zip file**. Choose the supplied ZIP; do not unzip it. For an untrusted build, Kodi may require temporarily enabling Unknown sources. You may need to transfer the ZIP via a file manager on Fire TV.
2. Open **Add-ons → Video add-ons → Callen Prime Theatre (CP02 Demo)**. Confirm that fictional demo rows appear. Select **Check current profile isolation**; neutral is expected before activation.
3. While using the current Kodi profile, select **Activate ANDY demo in THIS Kodi profile** (for your profile). Switch to the other Kodi profile using Kodi's own profile controls and select **Activate DAD demo in THIS Kodi profile**. Names here select only *fictional data*. Check the profile status again.
4. Open **Nimbus Settings → Home / Widgets**, and choose the Movies or desired custom home category's widget editor. Add exactly five widgets via the Callen Prime add-on's directory entries if Nimbus offers the normal add-on path picker. Select: Continue Watching, What's New, Based on Your Watching, Fresh for You, Discover Something Different.
5. If Nimbus permits direct plugin paths rather than using its browse picker, use the five URIs exactly as written in [CP02 architecture](CP02-ARCHITECTURE.md). Keep order and titles fixed. Do not attempt to make row headings rotate in CP02.
6. Apply Nimbus configuration **once** and allow any one-time skin reload. Navigate to Home. The content should show `[CP02 DEMO]` labels and three reusable placeholder poster designs. Selecting a title should show a message, never play video.
7. If you cannot obtain five independent rows through the stock Nimbus editor, **record that fact and stop**. Do not install unverified third-party editors, manually modify Nimbus XML, or repeatedly reload the skin to force success.

### Optional P0/P1 comparison

Configure a temporary single widget with `plugin://plugin.video.callenprime/?row=frozen`; measure. Change only its source to `plugin://plugin.video.callenprime/?row=probe`, keeping layout and assets identical. This is a diagnostic plugin comparator, not one of the five normal rows.

### Rollback (no Kodi reset)

1. Restore the previous widget settings from the screenshots/notes you recorded. Allow Nimbus to reload **only if it normally does so while applying settings**.
2. Confirm Home and existing authorised media add-ons still behave normally.
3. Disable/remove **Callen Prime Theatre (CP02 Demo)** in Kodi Add-ons. Delete its user data only if you wish to clear the fictional preset. Your other add-on data, logins and libraries are not part of the CP02 package.
4. If a widget remains, remove its Callen Prime path in Nimbus. Do **not** clear Kodi userdata or uninstall Kodi to fix this test.
