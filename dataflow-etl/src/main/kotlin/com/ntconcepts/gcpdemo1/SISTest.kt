package com.ntconcepts.gcpdemo1

import org.apache.sis.referencing.CommonCRS
import org.apache.sis.referencing.GeodeticCalculator


fun main(args: Array<String>) {
    val crs = CommonCRS.WGS84.universal(41.8839, -87.6319)


    val calc = GeodeticCalculator.create(crs)
    calc.setStartGeographicPoint(41.8839, -87.6319)
    calc.setEndGeographicPoint(41.938391258, -87.63857492)

    println(calc.geodesicDistance)
    println(calc.distanceUnit)

//    val operation = CRS.findOperation(sourceCRS, targetCRS, null)
//
//    val ptSrc = DirectPosition2D(40.0, 14.0)           // 40°N 14°E
//    val ptDst = operation.mathTransform.transform(ptSrc, null)
//
//    println("Source: $ptSrc")
//    println("Target: $ptDst")
}