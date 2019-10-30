package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV
import org.apache.beam.sdk.values.TupleTag
import java.awt.geom.Point2D

class CenteredLatLongFn(
    val mapCenterLat: ValueProvider<Double>,
    val mapCenterLong: ValueProvider<Double>,
    val tripsWithCenteredCoords: TupleTag<KV<TaxiRideL1, TaxiTripOutput>>,
    val startLats: TupleTag<Double>,
    val startLongs: TupleTag<Double>
) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

    private lateinit var mapCenterPoint: Point2D.Double

    private fun initCenterPoint(lat: Double, long: Double) {
        if (!::mapCenterPoint.isInitialized) {
            mapCenterPoint = Point2D.Double(long, lat)
        }
    }

    @StartBundle
    fun start(c: StartBundleContext) {
        initCenterPoint(mapCenterLat.get(), mapCenterLong.get())
    }

    @ProcessElement
    fun apply(c: ProcessContext, out: MultiOutputReceiver) {

        val trip = c.element().key
        val row = c.element().value.copy()

        if (trip?.pickup_latitude != null) {
            //Calculate centered
            row.pickup_lat_centered = mapCenterPoint.y - trip.pickup_latitude
//            out.get(startLats).output(row.pickup_lat_centered)
            out.get(startLats).output(trip.pickup_latitude)
        }

        if (trip?.pickup_longitude != null) {
//Calculate centered
            row.pickup_long_centered = mapCenterPoint.x - trip.pickup_longitude
//            out.get(startLongs).output(row.pickup_long_centered)
            out.get(startLongs).output(trip.pickup_longitude)
        }

        out.get(tripsWithCenteredCoords).output(KV.of(trip, row))

    }
}