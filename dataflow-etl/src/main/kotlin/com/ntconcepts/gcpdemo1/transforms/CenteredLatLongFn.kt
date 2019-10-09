package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV
import org.apache.beam.sdk.values.TupleTag
import java.awt.geom.Point2D

class CenteredLatLongFn(
    val mapCenterPoint: ValueProvider<Point2D.Double>,
    val tripsWithCenteredCoords: TupleTag<KV<TaxiRideL1, TaxiTripOutput>>,
    val startLats: TupleTag<Double>,
    val startLongs: TupleTag<Double>
) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

    @ProcessElement
    fun apply(c: ProcessContext, out: MultiOutputReceiver) {

        val trip = c.element().key
        val row = c.element().value.copy()

        if (trip?.pickup_latitude != null) {
            //Calculate centered
            row.pickup_lat_centered = mapCenterPoint.get().y - trip.pickup_latitude
            out.get(startLats).output(row.pickup_lat_centered)
        }

        if (trip?.pickup_longitude != null) {
//Calculate centered
            row.pickup_long_centered = mapCenterPoint.get().x - trip.pickup_longitude
            out.get(startLongs).output(row.pickup_long_centered)
        }

        out.get(tripsWithCenteredCoords).output(KV.of(trip, row))

    }
}