package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV
import org.apache.beam.sdk.values.PCollectionView
import org.apache.sis.referencing.CommonCRS
import org.apache.sis.referencing.GeodeticCalculator
import org.opengis.referencing.crs.ProjectedCRS
import java.awt.geom.Point2D

class TransformLatLongFn(
    private val maxLatView: PCollectionView<Double>,
    private val minLatView: PCollectionView<Double>,
    private val maxLongView: PCollectionView<Double>,
    private val minLongView: PCollectionView<Double>,
    private val stdPickupLatView: PCollectionView<Double>,
    private val stdPickupLongView: PCollectionView<Double>,
    private val meanPickupLatView: PCollectionView<Double>,
    private val meanPickupLongView: PCollectionView<Double>,
    private val mapCenterLat: ValueProvider<Double>,
    private val mapCenterLong: ValueProvider<Double>
) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

    lateinit var crs: ProjectedCRS
    private lateinit var mapCenterPoint: Point2D.Double

    private fun initCRS() {
        if (!::crs.isInitialized) {
            crs = CommonCRS.WGS84.universal(mapCenterPoint.y, mapCenterPoint.x)
        }
    }

    private fun initCenterPoint(lat: Double, long: Double) {
        if (!::mapCenterPoint.isInitialized) {
            mapCenterPoint = Point2D.Double(long, lat)
        }
    }

    @StartBundle
    fun start(c: StartBundleContext) {
        initCenterPoint(mapCenterLat.get(), mapCenterLong.get())
        initCRS()
    }

    @ProcessElement
    fun apply(c: ProcessContext) {

        val trip = c.element().key
        val row = c.element().value.copy()

        val maxPickupLat = c.sideInput(maxLatView)
        val minPickupLat = c.sideInput(minLatView)
        val maxPickupLong = c.sideInput(maxLongView)
        val minPickupLong = c.sideInput(minLongView)
        val stdPickupLat = c.sideInput(stdPickupLatView)
        val stdPickupLong = c.sideInput(stdPickupLongView)
        val meanPickupLat = c.sideInput(meanPickupLatView)
        val meanPickupLong = c.sideInput(meanPickupLongView)

//        if (trip?.pickup_latitude != null && trip.pickup_longitude != null) {
//            val calc = GeodeticCalculator.create(crs)
//            calc.setStartGeographicPoint(mapCenterPoint.y, mapCenterPoint.x)
//            calc.setEndGeographicPoint(trip.pickup_latitude, trip.pickup_longitude)
//            row.distance_from_center = calc.geodesicDistance / 1000
//        }

        if (trip?.pickup_latitude != null && row.pickup_lat_centered != null) {
            row.pickup_latitude = trip.pickup_latitude
            //Normalize lat between 0 and 1
            row.pickup_lat_norm =
                (row.pickup_latitude as Double - minPickupLat) / (maxPickupLat - minPickupLat)

            //Standardize lat
            row.pickup_lat_std =
                (row.pickup_latitude as Double - meanPickupLat) / stdPickupLat
        }
        if (trip?.pickup_longitude != null) {
            row.pickup_longitude = trip.pickup_longitude
            //Normalize long between 0 and 1
            row.pickup_long_norm =
                (row.pickup_longitude as Double - minPickupLong) / (maxPickupLong - minPickupLong)

            //Standardize lat
            row.pickup_long_std =
                (row.pickup_longitude as Double - meanPickupLong) / stdPickupLong
        }

        c.output(KV.of(trip, row))
    }

}