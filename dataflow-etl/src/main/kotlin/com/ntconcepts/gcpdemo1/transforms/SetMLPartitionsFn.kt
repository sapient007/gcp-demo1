package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import com.ntconcepts.gcpdemo1.utils.RandomCollection
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV

class SetMLPartitionsFn(
    private val mlPartitionTrainWeight: ValueProvider<Double>,
    private val mlPartitionTestWeight: ValueProvider<Double>,
    private val mlPartitionValidationWeight: ValueProvider<Double>
) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

    private val weights = RandomCollection<String>()

    @StartBundle
    fun setupWeights() {
        if (weights.size() == 0) {
            weights.add(mlPartitionTrainWeight.get(), "train")
            weights.add(mlPartitionTestWeight.get(), "test")
            weights.add(mlPartitionValidationWeight.get(), "validation")
        }
    }

    @ProcessElement
    fun apply(c: ProcessContext) {
        val row = c.element().value.copy()
        row.ml_partition = weights.next()
        c.output(KV.of(c.element().key, row))
    }


}