# nótt
## standalone [mlr](https://monome.org/docs/norns/dust/tehn/mlr/) & [norns](https://monome.org/norns/) inspired (granular) audio looper

## Usage

[Click here for detailed info.](./docs/USAGE.md)

## Hardware

- 1x Raspberry Pi 3B+
- 8x [Adafruit NeoTrellis](https://www.adafruit.com/product/3954)
- 8x [Elastomer for NeoTrellis](https://www.adafruit.com/product/1611)
- 1x [Blokas Pisound](https://blokas.io/pisound)

1. solder NeoTrellis into 2x4 grid
    * remember about [addressing](https://learn.adafruit.com/adafruit-neotrellis/tiling#addressing-2-11)
    * you can edit (and see my) address in [`./ui/ui.py`](./ui/ui.py) file
2. solder NeoTrellis to [Pisound GPIO](https://blokas.io/pisound/docs/Specs/#raspberry-pi-pins-used-by-pisound):

    | NeoTrellis | Pisound      |
    |------------|--------------|
    | `GND`      | `GND`: `1`   |
    | `VIN`      | `3.3V`: `4`  |
    | `SDA`      | `BCM2`: `13` |
    | `SCL`      | `BCM3`: `14` |
    | `INT`      | `BCM5`: `5`  |

## Installation

1. setup Raspbian Lite on SD Card
2. ssh into Raspberry Pi
3. setup Pisound: `curl https://blokas.io/pisound/install-pisound.sh | sh`
4. enable i2c in `raspi-config`
5. install python deps:

  ```bash
  sudo apt-get install python3-pip
  sudo pip3 install --upgrade setuptools

  sudo apt-get install -y python-smbus
  sudo apt-get install -y i2c-tools
  sudo apt-get install -y python3-liblo

  pip3 install RPI.GPIO
  pip3 install adafruit-blinka
  pip3 install adafruit-circuitpython-neotrellis
  ```

6. install chuck from source:

  ```bash
  mkdir ~/temp && cd ~/temp

  git clone https://github.com/ccrma/chuck.git chuck-git

  # line 3788 replace `0` with `loop_start[0]` (https://github.com/ccrma/chuck/pull/115/files)
  # I should make a patch, but I'm too lazy
  vim chuck-git/src/core/ugen_xxx.cpp

  sudo apt-get install bison flex libasound2-dev libsndfile1-dev

  cd chuck-git/src/
  make linux-alasa

  mkdir ~/.bin
  cp chuck ~/.bin/chuck
  ```

7. `git clone git@github.com:szymonkaliski/nott.git ~/app && cd ~/app`
8. `./scripts/systemd-setup.sh`
9. `./scripts/systemd-start.sh`

## Case

The STL & SVG files are available in [`./case/dist`](./case/dist) folder. I laser-cut mine in plexi.

If you want to work on the case:

1. `cd ./case`
2. `npm i`
3. open `model.js`
4. open `http://localhost:3000`

Case was designed in [modeler](https://github.com/szymonkaliski/modeler).
