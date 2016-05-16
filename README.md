# buspirate_SSD1306

Python3 module for SSD1306 OLED 128x64 Display (https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf#page=37&zoom=auto,0,842) with Bus Pirate (http://dangerousprototypes.com/docs/Bus_Pirate)

## Usage

```
python -m buspirate_SSD1306 <DEVICE>
```

Running display with Bus Pirate on _/dev/ttyUSB0_

## Example

```
import psutil, sys
from datetime import datetime

# attach to bus pirate on ttyUSB0
d = BusPirateSSD1306(device='/dev/ttyUSB0', baud=115200)

# setup display
d.init()

# clear content
d.clear()

# prepare layout
d.setCursorPosition(0, 2)
d.println('CPU:')
d.println('MEM:')

d.setCursorPosition(0, 5)
d.println('Net stats in MB')
d.println('Snt:')
d.println('Rcv:')

while True:
  # update values
	d.setCursorPosition(0, 0)
	d.println(datetime.now().strftime('%Y/%m/%d'))
	d.println(datetime.now().strftime('%H:%M:%S'))

	d.setCursorPosition(5, 2)
	d.print('%3.1f  ' % (psutil.cpu_percent()))
	d.setCursorPosition(5, 3)
	d.print('%3.1f  ' % (psutil.virtual_memory().percent))

	d.setCursorPosition(5, 6)
	d.print('%i  ' % (psutil.net_io_counters().bytes_sent/1048576))
	d.setCursorPosition(5, 7)
	d.print('%i  ' % (psutil.net_io_counters().bytes_recv/1048576))
```
