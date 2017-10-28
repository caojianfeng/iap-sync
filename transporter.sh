#! /bin/sh

transporter=`find "$(dirname $(xcode-select -p))/Applications/Application Loader.app/Contents" -name  iTMSTransporter | sed -E 's/[[:space:]]/\\ /g'`
"$transporter" $*

