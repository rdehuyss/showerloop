# Showerloop NG

This is the source code repository for showerloop NG, an updated version of [showerloop](https://showerloop.org) which is girlfriend/wife approved.

> The idea is simple: collect, clean and reuse the hot water from your shower that normally flows down the drain.   

##How does it work?
1. Using water flow sensors on both the cold and hot water supply, we see whether somebody is showering
2. If water flow is detected, we wait until the hot water is warm enough using a temperature sensor
3. If the hot water supply is hot enough, we close the drain valve
4. Once there is enough water collected (detected using a water level sensor):
   1. the water pump starts and builds pressure
   2. a UVC lamp starts to kill viruses and bacterias
   3. the cold water supply valve closes
   4. the recuperation water supply opens
5. You can enjoy a really nice, warm and long shower. Thanks to the use of a thermostatic shower valve, only a bit of warm water is used to keep the water temperature constant. The two water level sensors keep the water level constant and open the drain valve a bit, if needed.
6. Once you stop your shower (this is again detected by the water flow sensors), the following happens:
   1. the water pump stops
   2. the uvc lamp switches off
   3. the drain valve opens
   4. the recuperation water valve closes
   5. the cold water valve opens
7. And everything is ready for your next shower!

##Warning
* This is a work in progress, there will probably still be some bugs in the software
* You are combining 220V with water. If you're not experienced in electricity and plumbing, please stop now
* The hardware items may not be final
* I do not take any responsibility whatsoever when you try to build this yourself 

##Video showing the shower prototype
[Here is a video showing a working prototype of showerloop](https://lh3.googleusercontent.com/RiQwsrnvpodZIGrsXgYXlvrhQmIinLnbh-OmgbJ6Kly4MkZ-bXnuI9YJNUxAbHXJ9iAuCArBEZaFzNuW3NdeOmrP6EqaUUFchiInSAtR1N4IVFcJKaVCW6QOi1JR51bOhtPEBZcEYgI)

## Part list:
* PVC Tubing
* [DN40 Electric Motorized PVC Water Valve](https://www.aliexpress.com/item/misol-motorized-pvc-valve-12V-DN40-BSP-1-5-PVC-valve-2-way-electrical-pvc-valve/32808969861.html?spm=a2g0s.9042311.0.0.27424c4d3bYL2D)
* [DN20 Electric Motorized Brass Water Valve](https://www.aliexpress.com/item/Shipping-Free-Hot-Sales-12VDC-3-Control-Wires-Brass-3-4-DN20-Electric-Motorized-Valve-BSP/32800474627.html?spm=a2g0s.9042311.0.0.157c4c4d98rarg) x 2
* [Hall-based Water Flow Sensor](https://www.aliexpress.com/item/G1-2-Copper-Water-Flow-Sensor-Hall-Sensor-Water-Control-1-25-L-min-DN15-Port/32700922635.html?spm=a2g0s.9042311.0.0.157c4c4d98rarg) x 2
* [Contactless Liquid Water Level Sensor](https://www.aliexpress.com/item/Contactless-Liquid-Water-Level-Sensor-Non-contact-Level-Detector-Module-Output-High-or-Low-level-with/32807115210.html?spm=a2g0s.9042311.0.0.157c4c4d98rarg) x 2
* [Water Filter](https://www.aliexpress.com/item/Prefilter-water-filter-First-step-of-water-purifier-system-59-brass-40micron-stainless-steel-mesh-prefiltro/32785050045.html?spm=a2g0s.9042311.0.0.157c4c4d98rarg)
* [UVC Sterilizer Lamp](https://www.aliexpress.com/item/JEBO-Aqua-UV-Sterilizer-Lamp-Light-Ultraviolet-Filter-Clarifier-Water-Cleaner-For-Aquarium-Pond-Coral-Koi/32835644485.html?spm=a2g0s.9042311.0.0.27424c4d3bYL2D)
* [Water Pump](https://www.aliexpress.com/item/Jebao-Jecod-DCP3000-DCP4000-Powerful-Water-Pump-Sine-Wave-Super-Quiet-Return-Pump-W-Controller-Frequency/32827538343.html?spm=a2g0s.9042311.0.0.157c4c4d98rarg)
* [ESP32 Wemos Lolin](https://www.aliexpress.com/item/4-MB-Flash-WEMOS-Lolin32-V1-0-0-WIFI-Bluetooth-Card-Based-ESP-32-ESP-WROOM/32852023085.html?spm=2114.search0104.3.15.4e04da6fSytFrt&ws_ab_test=searchweb0_0,searchweb201602_1_10152_10151_10065_10068_10344_10342_10343_10340_10341_10696_10084_10083_10618_10304_10307_10820_10821_10302_10843_10059_100031_10103_10624_10623_10622_10621_10620,searchweb201603_51,ppcSwitch_2&algo_expid=09912ab8-6aa3-4d3b-8b8f-b376802a110b-2&algo_pvid=09912ab8-6aa3-4d3b-8b8f-b376802a110b&transAbTest=ae803_2&priceBeautifyAB=0)
* Relay boards

## Build instructions
will follow... first a PCB design is needed


    


For download
=> https://api.github.com/repos/rdehuyss/showerloop/releases/latest
=> get tag

https://api.github.com/repos/rdehuyss/showerloop/contents/current?ref=refs/tags/v0.1
