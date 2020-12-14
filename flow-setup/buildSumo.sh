#/bin/bash
cd ~
git clone https://github.com/eclipse/sumo.git
cd sumo
git checkout 2147d155b1
make -f Makefile.cvs

./configure CPPFLAGS='-D ACCEPT_USE_OF_DEPRECATED_PROJ_API_H' # This is the important line
make -j$nproc
echo 'export SUMO_HOME="$HOME/sumo"' >> ~/.bashrc
echo 'export PATH="$HOME/sumo/bin:$PATH"' >> ~/.bashrc
echo 'export PYTHONPATH="$HOME/sumo/tools:$PYTHONPATH"' >> ~/.bashrc
source ~/.bashrc
