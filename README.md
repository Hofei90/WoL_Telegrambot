# WoL_Telegrambot

## Ziel des Projektes

Der WoL (Wake on Lan) Telegram Bot lässt Geräte mit Hilfe von
Magic Pakets starten.

### Ablauf

Nach senden eines Botkommandos an den Telegrambot erhält man eine Liste von allen in der wol_cfg.toml eingetragenen 
Geräte. Nach Auswahl eines Gerätes wird das Gerät mit Hilfe eines generierten Magic Paket gestartet.
Anschließend wird mit Hilfe von arp die zugehörige IP Adresse ermittelt und versucht das Gerät zu pingen.
Ist der Ping in einer bestimmten Zeit erfolgreich, oder nicht oder lässt sich die IP nicht ermitteln erhält man die
entsprechende Nachricht.

## Einrichtung


Das zu startende Gerät muss für Wake on Lan konfiguriert sein. Wie dies für das entsprechende Gerät einzurichten ist, 
kann an dieser Stelle nicht erklärt werden aufgrund der vielfalt an Geräten.

Bei Telegram Botfather einen neuen Telegrambot erstellen und den Bottoken für die Konfiguration bereithalten


### Installation

Zur Ausführung des Skriptes wird Python >= 3.6 vorausgesetzt
Die Anleitung bezieht sich auf die Einrichtung auf einem Raspberry Pi mit Buster.


```code 
git clone https://github.com/Hofei90/WoL_Telegrambot.git /home/pi/wol_telegrambot
cd /home/pi/wol_telegrambot
pip3 install --user -r requirements.txt
```

### Konfiguration

```code
nano wol_cfg.toml
```
Die entsprechenden Felder ausfüllen. `<>` gehören ersetzt. `""` Müssen stehen bleiben
In dem Feld allowed_id werden alle Telegramids eingetragen, welche den Bot verwenden dürfen.
Die ID kann beispielsweise mit dem Telegram Raw Bot ermittelt werden.

## Inbetriebnahme

### Erster Test:

`python3 wol_bot.py` ausführen

Wenn dieser erster Erfolgreich verläuft und man mit dem Bot Kontakt aufnehmen kann, so kann man als Abschluss noch einen 
Autostart mit Systemd vorbereiten.



### Service Unit erstellen

Ausführung erfordert root Rechte

`nano /etc/systemd/system/wol_telegrambot.service`

```code
[Unit]
Description=Service Unit zum starten des WoL Telegrambotes
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/wol_telegrambot/wol_bot.py
User=pi


[Install]
WantedBy=multi-user.target
```

```code 
chmod 644 /etc/systemd/system/wol_telegrambot.service
systemctl start smartmeter.service
```

Kontrolle ob Skript nun wieder aktiv ist, wenn ja automatische Ausführung anlegen:

`systemctl enable smartmeter.service`