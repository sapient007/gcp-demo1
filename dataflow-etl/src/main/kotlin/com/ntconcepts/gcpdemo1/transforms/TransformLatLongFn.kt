package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV
import org.apache.beam.sdk.values.PCollectionView

class TransformLatLongFn(val maxLatView: PCollectionView<Double>) :
    DoFn<KV<TaxiRideL1, TableRow>, KV<TaxiRideL1, TableRow>>() {

    @ProcessElement
    fun apply(c: ProcessContext, out: MultiOutputReceiver) {

        val trip = c.element().key
        val row = c.element().value

        val maxPickupLat = c.sideInput(maxLatView)

        c.output(KV.of(trip, row))
    }

}