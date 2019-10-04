package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.TupleTag
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class FilterRowsFn(val startLats: TupleTag<Double>, val startLongs: TupleTag<Double>, val trips: TupleTag<TaxiRideL1>) :
    DoFn<TaxiRideL1, TaxiRideL1>() {

    lateinit var log: Logger

    private fun initLogger() {
        log = LoggerFactory.getLogger(FilterRowsFn::class.java)
    }

    @ProcessElement
    fun apply(c: ProcessContext, out: MultiOutputReceiver) {
        initLogger()
        val trip = c.element()

//        if(trip.payment_type == "Dispute" || trip.payment_type == "Mobile") {
//            trip.payment_type = "Credit Card"
//        }

        if (
            (trip != null) &&
            (trip.trip_miles != null && trip.trip_miles > 0) &&
            (trip.trip_seconds != null && trip.trip_seconds > 0) &&
            (trip.fare != null && trip.fare > 0) &&
            (trip.payment_type == "Cash" || trip.payment_type == "Credit Card") &&
            (trip.trip_start_timestamp != null && trip.trip_start_timestamp > 0L) &&
            (trip.pickup_latitude != null && trip.pickup_latitude > 0.0) &&
            (trip.pickup_longitude != null && trip.pickup_longitude > 0.0)
        ) {
            out.get(trips).output(trip)
            out.get(startLats).output(trip.pickup_latitude)
            out.get(startLongs).output(trip.pickup_longitude)
        }
        else {
            log.info(trip.toString())
        }
    }
}