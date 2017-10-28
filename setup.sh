#! /bin/bash

if [[ ! -d "./ENV" ]] ; then
  mkdir "ENV"
fi

if [ ! -f ENV/python3/bin/python ] ;then
  virtualenv -p python3 ENV/python3  && source ENV/python3/bin/activate && pip install -r requirements.txt
fi


