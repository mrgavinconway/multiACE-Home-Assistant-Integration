# multiACE Home Assistant integration

Custom Home Assistant integration for the multiACE Web API on Snapmaker U1 printers.

## Features

- Shows the current multiACE printer state, mode, active ACE, ACE temperature, and dryer status.
- Creates filament slot sensors for up to 4 ACE units with material, brand, subtype, color, RFID state, and loaded toolhead attributes.
- Creates toolhead sensors showing which ACE and slot currently feed each toolhead.
- Creates dryer controls for each connected ACE. Set the dryer duration and temperature on the device page, then turn on the ACE dryer switch to send `ACE_DRY`. Turning it off sends `ACE_STOP_DRYING`.

## Installation

### HACS (recommended)

1. Open **HACS** in Home Assistant.
2. Open the three-dot menu in the top-right corner and choose **Custom repositories**.
3. Add this repository URL:

   ```text
   https://github.com/mrgavinconway/multiACE-Home-Assistant-Integration
   ```

4. Set the category to **Integration**, then select **Add**.
5. Find **multiACE Home Assistant Integration** in HACS and download it. HACS only installs the integration files; it does not configure your printer.
6. Restart Home Assistant.
7. Go to **Settings > Devices & services > Add integration** and search for **multiACE**.
8. Enter your printer address when prompted.

Use your printer hostname or IP address:

```text
http://yourprinter/multiace/
```

### Manual

Copy `custom_components/multiace` into your Home Assistant `custom_components` directory and restart Home Assistant. Then go to **Settings > Devices & services > Add integration**, search for **multiACE**, and add it there.

When prompted, use your printer hostname or IP address:

```text
http://yourprinter/multiace/
```

The integration polls `/multiace/api/state` locally every 15 seconds. Dryer switch defaults are 50 C for 240 minutes. Each connected ACE also has dryer duration and temperature controls on the device page.

## Credits

This Home Assistant integration is built for the multiACE Web API and depends on the upstream multiACE project by decay71 / postapocalyptic-diy:

- https://github.com/decay71/multiACE
- https://postapocalyptic-diy.com/multiace/

All credit for multiACE itself, including the Snapmaker U1 / ACE Pro multi-filament control system and Web API this integration talks to, belongs to the upstream multiACE author and contributors.
