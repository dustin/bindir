#!/bin/csh
# Set the java classpath.

if(-d ${HOME}/lib/java) then
	setenv CLASSPATH ""
	foreach i (${HOME}/lib/java/*.jar)
		setenv CLASSPATH "${CLASSPATH}${i}:"
	end
	setenv CLASSPATH "${CLASSPATH}."
endif
