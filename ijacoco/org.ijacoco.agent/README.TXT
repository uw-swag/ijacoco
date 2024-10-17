This bundle provides the coverage agent "ijacocoagent.jar" as a resource. The
agent JAR is created as part of the build process and therefore not available in
the source tree. Which means this bundle is incomplete when directly used in the
Eclise IDE. If you want to use the bundle org.ijacoco.agent within the IDE,
please run the local build (see documentation) first.

The ijacocoagent.jar file is created by the build at 

  /org.ijacoco.agent/target/classes/ijacocoagent.jar
  
and linked by this project.
