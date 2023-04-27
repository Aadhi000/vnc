if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/Aadhi000/vnc.git /vnc
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /vnc
fi
cd /vnc
pip3 install -U -r requirements.txt
echo "Starting Ajax 💥..."
python3 bot.py
