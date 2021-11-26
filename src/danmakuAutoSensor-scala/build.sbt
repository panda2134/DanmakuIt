name := "danmakuAutoSensor"

version := "0.1"

scalaVersion := "2.13.7"

idePackagePrefix := Some("site.panda2134.danmakuit")

libraryDependencies ++= List("com.softwaremill.sttp.client3" %% "core" % "3.3.16",
  "com.softwaremill.sttp.client3" %% "async-http-client-backend-future" % "3.3.16",
  "com.softwaremill.sttp.client3" %% "json4s" % "3.3.16",
  "org.json4s" %% "json4s-native" % "4.0.2",
  "org.apache.pulsar" % "pulsar-functions-api" % "2.8.1")