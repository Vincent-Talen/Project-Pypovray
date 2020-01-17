Authors: Reindert Visser and Vincent Talen
Date: 17 jan 2020
Version 2.0


Name
Animating RNA Splicing


Description
This program animates a short animation of a minute that explains and shows how RNA splicing works.
It is written in Python 3.7.3 and uses the Vapory and PyPov-RAY modules to render the scenes.
See the included 'rna_splicing.mp4' for the result that this script gives.


Installation
The easiest way to to run this script is on a Linux platform, it was made on a platform running Debian Linux 10.x (Codename 'Buster').
At first you will need to install Python, it was written with Python 3.7.3
There will also need to be installed the pypovray and vapory modules, for their installation manuals see link 1.
Drag the script 'eindopdracht_ReinderVisser_VincentTalen.py' in the folder where you installed pypovray.
To run this particular script you will need to included 'default.ini' to be the selected config, otherwise the settings will not be correct.
The included 'my_models.py' also needs to be placed inside the vapory folder because there are custom models used that get imported.
If you've done all this correctly this script should be able to run.


Usage
To use this script simply open a command shell and go to the correct file directory where you installed pypovray.
Once in the correct directory you can type 'python3 eindopdracht_ReindertVisser_VincentTalen.py' in the command line and run it.
If you are running it for the first time it won't ask anything but if you're running it for the second time it will ask to delete the previously rendered images and movie.
Simply type 'y' and press enter, this will need to be done twice.


Support
Link 1, Pypovray/vapory installation: https://bitbucket.org/mkempenaar/pypovray/src/master/
Link 2, Python 3.7.3: https://www.python.org/downloads/release/python-373/
For further questions send an email to v.k.talen@st.hanze.nl or r.f.visser@st.hanze.nl


Authors and acknowledgment
Marcel Kempenaar for providing the modules.
Arne Poortinga for being ready to help if needed.
