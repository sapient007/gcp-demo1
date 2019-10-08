package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import com.ntconcepts.gcpdemo1.utils.RandomCollection
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV

class SetMLPartitionsFn(val mlPartionWeights: ValueProvider<HashMap<String, Double>>) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

    private val weights = RandomCollection<String>()

    private fun setupWeights() {
        if (weights.size() == 0) {
            val ws = mlPartionWeights.get()
            ws.forEach {
                weights.add(it.value, it.key)
            }
        }
    }

    @ProcessElement
    fun apply(c: ProcessContext) {
        setupWeights()
        val row = c.element().value.copy()
        row.ml_partition = weights.next()
        c.output(KV.of(c.element().key, row))
    }


}