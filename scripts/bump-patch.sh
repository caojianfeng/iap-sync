#! /bin/sh

script_name=`which $0`
if [ "x`echo $script_name | grep -e '^\/'`" = "x" ] ; then
  script_path=`pwd`/${script_name}
else
  script_path=${script_name}
fi

project_root=$(dirname $(dirname "${script_path}"))
setup_py="${project_root}/setup.py"

versions=(`git log -E --pretty=tformat:%s --grep='^[[:space:]]*[0-9]+\.[0-9]+\.[0-9]+' | awk '{ print $1 }' | sed -e 's/[^0-9.]//g'`)

latest=${versions[0]}
parts=(`echo "${latest}" | tr "." " "`)
patch=${parts[2]}
parts[2]=`expr "${patch}" '+' 1`

ret=`echo ${parts[*]} | tr " " '.'`
echo $ret
