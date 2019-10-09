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
    val maxLatView: PCollectionView<Double>,
    val minLatView: PCollectionView<Double>,
    val maxLongView: PCollectionView<Double>,
    val minLongView: PCollectionView<Double>,
    val stdPickupLatView: PCollectionView<Double>,
    val stdPickupLongView: PCollectionView<Double>,
    val meanPickupLatView: PCollectionView<Double>,
    val meanPickupLongView: PCollectionView<Double>,
    val mapCenterPoint: ValueProvider<Point2D.Double>
) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

    lateinit var crs: ProjectedCRS

    private fun initCRS(mapCenterPoint: Point2D.Double) {
        if (!::crs.isInitialized) {
            crs = CommonCRS.WGS84.universal(mapCenterPoint.y, mapCenterPoint.x)
        }
    }

    @ProcessElement
    fun apply(c: ProcessContext) {
        initCRS(mapCenterPoint.get())

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

        if (trip?.pickup_latitude != null && trip.pickup_longitude != null) {
            val calc = GeodeticCalculator.create(crs)
            calc.setStartGeographicPoint(mapCenterPoint.get().y, mapCenterPoint.get().x)
            calc.setEndGeographicPoint(trip.pickup_latitude, trip.pickup_longitude)
            row.distance_from_center = calc.geodesicDistance / 1000
        }

        if (trip?.pickup_latitude != null && row.pickup_lat_centered != null) {
            row.pickup_latitude = trip.pickup_latitude
            //Normalize lat between 0 and 1
            row.pickup_lat_norm =
                (row.pickup_lat_centered as Double - minPickupLat) / (maxPickupLat - minPickupLat)

            //Standardize lat
            row.pickup_lat_std =
                (row.pickup_lat_centered as Double - meanPickupLat) / stdPickupLat
        }
        if (trip?.pickup_longitude != null) {
            row.pickup_longitude = trip.pickup_longitude
            //Normalize long between 0 and 1
            row.pickup_long_norm =
                (row.pickup_long_centered as Double - minPickupLong) / (maxPickupLong - minPickupLong)

            //Standardize lat
            row.pickup_long_std =
                (row.pickup_long_centered as Double - meanPickupLong) / stdPickupLong
        }

        c.output(KV.of(trip, row))
    }

}