# multiACE Home Assistant integration

Custom Home Assistant integration for the multiACE Web API on Snapmaker U1 printers.

## Features

- Shows the current multiACE printer state, mode, active ACE, ACE temperature, and dryer status.
- Creates filament slot sensors for up to 4 ACE units with material, brand, subtype, color, RFID state, and loaded toolhead attributes.
- Creates toolhead sensors showing which ACE and slot currently feed each toolhead.
- Creates one dryer switch per possible ACE. Turning a switch on sends `ACE_DRY`; turning it off sends `ACE_STOP_DRYING`.

## Install

Copy `custom_components/multiace` into your Home Assistant `custom_components` directory, restart Home Assistant, then add **multiACE** from **Settings > Devices & services**.

Use your printer hostname or IP address:

```text
http://yourprinter/multiace/
```

The integration polls `/multiace/api/state` locally every 15 seconds. Dryer switch defaults are 50 C for 240 minutes and can be changed from the integration options.

## Credits

This Home Assistant integration is built for the multiACE Web API and depends on the upstream multiACE project by decay71 / postapocalyptic-diy:

- https://github.com/decay71/multiACE
- https://postapocalyptic-diy.com/multiace/

All credit for multiACE itself, including the Snapmaker U1 / ACE Pro multi-filament control system and Web API this integration talks to, belongs to the upstream multiACE author and contributors.
