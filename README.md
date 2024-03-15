# TechLife Bulb - Custom Integration for Home Assistant
This light integration controls your techlife bulbs without flashing or modifying.

## About this repository

The steps explained in this file are the ones I took to solve the problem of integrating my TechLife bulbs with Home Assistant. My Home Assistant instance is being run in a docker container.

## Features:
Ability to:
- Turn on / off
- Change brigthness
- Change rgb color

## Requirements:

In order to make the bulb (or bulbs) work you will need to:

- Connect the bulbs to your wifi
- Redirect bulb traffic to your custom mqtt broker
- Know which credentials are being used by the bulbs (username and password)
- Copy the folder custom_components into HA's config/custom_components folder
- Create lightbulb entities in your configuration.yaml file
- Restart HA

Don't forget to check the Credits and Info section at the end of this file.

## Connect the bulbs to your wifi

For this there are two options. Either use a script that others have created or configure it using the app. I believe I used the script once and it worked fine.

The script is `techlife_setup.py` and you can find it in the root of this repository. Check the `Connecting to wifi - Custom Script` section for more info.

The other option is to use the mobile app `TechLife Pro`. For this you will have to create an account and follow the steps listed there to connect the bulb to your wifi.

## Redirect bulb traffic to your custom mqtt broker

As far as I can tell, until 2020 there were two methods, now there is only one. I will be only explaining the one that is still working.

The method that is still working is to redirect the traffic from the bulbs to your custom mqtt broker. The traffic redirection is done via modifying the dns so that the name the bulb asks points to your mqtt broker. 

For this you will firstly need to run an mqtt broker. There are two options here, you could either run it inside the HA instance or either run it in a separate container. I chose the latter. I used the `eclipse-mosquitto` container.

Then you will have to run a dns server. Any dns server will be fine. I used **dnsmasq**. Due to my scenario I used it within a container, but is not necessary.

The configuration of the dns server should be redirecting the traffic from both ```cloud.qh-tek.com``` and ```cloud.hq-tek.com``` to your mqtt broker. The configuration file for dnsmasq should have the following lines:
```
address=/cloud.qh-tek.com/<your_mqtt_broker_ip>
address=/cloud.hq-tek.com/<your_mqtt_broker_ip>
```


## Obtain the credentials from your lightbulb

We are looking for three pieces of key information: mac address, username and password.

After my investigation I have concluded that both username and password are subject to change on manufacturing. When looking online I found that the most common username was `testuser` and the password was `testpassword`. This was not the case for me.

The mac address should be found in the router's configuration page. There you will have to be looking for a newly connected device and its mac address. The name of the device is something, again, subject to change. Mine was something like `TechLife-xxxx`.

The mac address format is: `00:00:00:00:00:00`

For debugging purposes also keep the lightbulb's IP address.

As for the username and password, we will be exploting the fact that the bulbs are trying to connect via unencrypted MQTT. We will have to capture the traffic the lightbulb sends when gets turned on and then inspect it. I used `tcpdump` to capture the traffic and then `wireshark` to inspect it. The username and password are sent in the clear.

The credentials my lightbulb was using were `user` and `passwd`.

For the lightbulb to use those credentials they must exist in the mqtt broker. Create a user with those credentials in the mqtt broker.

## Debugging

Once reached this point it is good to ensure that the connection is working properly. For that use the `tester.py` script and try to turn on and off the lightbulb. If it works then the credentials are correct and the traffic redirection is working.

Don't forget to change the data in the script to match your setup.

## Copy files into Home Assistant

The custom components are stored within config/custom_components/ folder. We will be creating the component techlife_bulb_control. The folder structure should be as follows:
```
config/custom_components/
└── techlife_bulb_control
    ├── __init__.py
    ├── light.py
    └── manifest.json
```

## Creating entity in configuration.yaml

Example configuration to create an entity called `light.yourbulb`.

``` yaml
light: 
    - platform: techlife_bulb_control
      mac_address: "00:00:00:00:00:00"
      name: "YourBulb"
      broker_url: 192.168.0.0
      broker_username: !secret broker_username
      broker_password: !secret broker_password
```

Note: the entity_id is given by the name.

## Restart Home Assistant

Once you have restarted, the custom_component will be available in your system (check home_assistant.log) and an entity named 'light.yourbulb' will be available.

Note that the entity can't be configured via the UI, only via the configuration.yaml file.

## Connecting to wifi - Custom Script

If the bulb is already connected to your wifi yoy can skip this step.
- Download 'techlife_setup.py'
- Ensure python installed in your system.
- Modify ssid, password and bssid inside the script.
- Connect the bulb (Reset if needed turning on / off 6 times)
- Connect your computer to the wifi made by the bulb
- Run `> python techlife_setup.py`

## Known issues
- The `TechLife Pro` will stop being able to reach the lightbulb once the traffic redirection is in place.
- At the time being there is no check for whether the lightbulb is online or not. HA will operate as if the lightbulb were always online.


## Credits and Info

The following links were used to either get information or plainly use their code. All credit is for them.

- Original posts:
  - https://community.openhab.org/t/hacking-techlife-pro-bulbs/85940
  - https://community.home-assistant.io/t/integrating-techlife-pro-light-bulbs-without-opening-or-soldering
- Github repos:
  - https://gist.github.com/Toniob/113246128adaa49fbbe61061d6c8fc6f
  - https://github.com/Marcoske23/TechLifePro-for-HA
  - https://github.com/thorin8k/techlife_bulb
- Documentation:
  - https://developers.home-assistant.io/docs/core/entity/light/
