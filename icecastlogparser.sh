#! /bin/bash


BASEDIR=/home/rama/dev/icecast-logs-parser     # script base dir
VALID_MD5=04cbfdbbd9b20e8b9ed1f3c1e830fffc
SCRIPT_NAME=icecastlogparser                   # script name without extension
SCRIPT=$BASEDIR/$SCRIPT_NAME.py                # full path to the script
SCRIPT_MD5=`md5sum $SCRIPT | awk '{print $1}'` # MD5SUM of the script

cd $BASEDIR
source venv/bin/activate

# check if the script matches 
if [ "$SCRIPT_MD5" == "$VALID_MD5" ]
then
	python $SCRIPT
else
	echo "ERROR: $SCRIPT MD5 sum changed (should be $VALID_MD5)"
	echo "       If you think this is not a security risk, just update it on the calling script."
fi
