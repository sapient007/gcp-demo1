package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV
import org.apache.beam.sdk.values.PCollectionView

class TransformLatLongFn(
    val maxLatView: PCollectionView<Double>,
    val minLatView: PCollectionView<Double>,
    val maxLongView: PCollectionView<Double>,
    val minLongView: PCollectionView<Double>,
    val stdPickupLatView: PCollectionView<Double>,
    val stdPickupLongView: PCollectionView<Double>,
    val meanPickupLatView: PCollectionView<Double>,
    val meanPickupLongView: PCollectionView<Double>
) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

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

        if (trip?.pickup_latitude != null) {
            row.pickup_latitude = trip.pickup_latitude
            //Normalize lat between 0 and 1
            row.pickup_lat_norm =
                (trip.pickup_latitude - minPickupLat) / (maxPickupLat - minPickupLat)

            //Standardize lat
            row.pickup_lat_std =
                (trip.pickup_latitude - meanPickupLat) / stdPickupLat

        }
        if (trip?.pickup_longitude != null) {
            row.pickup_longitude = trip.pickup_longitude
            //Normalize long between 0 and 1
            row.pickup_long_norm =
                (trip.pickup_longitude - minPickupLong) / (maxPickupLong - minPickupLong)

            //Standardize lat
            row.pickup_long_std =
                (trip.pickup_longitude - meanPickupLong) / stdPickupLong
        }

        c.output(KV.of(trip, row))
    }

}