import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    java
    application
    kotlin("jvm") version "1.3.50"
}

group = "com.ntconcepts"
version = "1.0-SNAPSHOT"

val beamVersion: String by project
val bigqueryVersion: String by project
val csvVersion: String by project
val sisVersion: String by project
val geoAPIVersion: String by project

allprojects {
    buildDir = File("C:/tmp/${rootProject.name}/${project.name}")
}

repositories {
    jcenter()
    mavenCentral()
}

dependencies {
    implementation(kotlin("stdlib-jdk8"))
    implementation("org.apache.beam:beam-sdks-java-core:$beamVersion")
    implementation("org.apache.beam:beam-runners-direct-java:$beamVersion")
    implementation("org.apache.beam:beam-runners-google-cloud-dataflow-java:$beamVersion")
    implementation("org.apache.beam:beam-sdks-java-io-google-cloud-platform:$beamVersion")
    implementation("com.google.cloud:google-cloud-bigquery:$bigqueryVersion")
    implementation("org.apache.commons:commons-csv:$csvVersion")
    implementation("org.apache.sis.core:sis-referencing:$sisVersion")
    implementation("org.opengis:geoapi:$geoAPIVersion")
    testCompile("junit", "junit", "4.12")
}

application  {
    mainClassName = "com.ntconcepts.gcpdemo1.MainKt"
}

tasks.getByName<JavaExec>("run") {
    if (project.hasProperty("args")) {
        val a = project.properties.get("args")
        if (a is String){
            args = a.split("\\s+".toRegex())
        }
    }
}

configure<JavaPluginConvention> {
    sourceCompatibility = JavaVersion.VERSION_1_8
}
tasks.withType<KotlinCompile> {
    kotlinOptions.jvmTarget = "1.8"
}
