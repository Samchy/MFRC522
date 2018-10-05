# MFRC522
add some features that Read/Write the M1/uid card from MFRC522 chip
1. add a dump read function read all sector

python sam_MFRC522.py r

python sam_MFRC522.py r -f r.dump

2. add a dunmp write funciton write all sector

//M1 card

python sam_MFRC522.py w -t 0 -f r.dump

//uid card

python sam_MFRC522.py w -t 1 -f r.dump

steps:

https://pimylifeup.com/raspberry-pi-rfid-rc522/
