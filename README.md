## First time setup
A functioning python 3 installation is required before continuing, anything will do but I recommend the [Anaconda version](https://www.anaconda.com/download/) of python 3. Anaconda is just a regular python install that comes with a large number of python libraries, and a system for installing libraries that are often difficult to install with pip.

## Requirements
The requirements can be installed with pip using

```pip install -r requirements.txt```

note: I used the [pipreqs tool](https://github.com/bndr/pipreqs) to generate the requirements file

You will also be required to install the NI Visa software available for free on their website
Additionally you will need libusb, information can be found on [the libusb website](https://libusb.info)

## Adding functions to devices
When adding a new function remember to register it inside the instruments ```__init__```. Below is an example
```python
self.register(self.SetStandardSquareWave, 'Standard\nSquare Wave', parameters = ["Frequency"])
```
This registers a function ```SetStandardSquareWave``` with the label ```Standard\nSquare Wave``` and specifies that it takes one parameter "Frequency". Currently a function can only have 1 parameter but eventually we'd like to support commands that accept an arbitrary number and the list format here lays the foundation for that.
