package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.avro.generic.GenericRecord
import org.apache.avro.generic.GenericRecordBuilder
import org.apache.beam.sdk.transforms.SimpleFunction
import org.apache.beam.sdk.values.KV

class OutputTaxiTripOutputFn : SimpleFunction<KV<TaxiRideL1, TaxiTripOutput>, GenericRecord>() {

    override fun apply(wrapper: KV<TaxiRideL1, TaxiTripOutput>): GenericRecord {
        val record = GenericRecordBuilder(wrapper.value.getSchema())
            .set("cash", wrapper.value.cash)
            .set("year", wrapper.value.year)
            .set("start_time_epoch", wrapper.value.start_time_epoch)
            .set("trip_miles", wrapper.value.trip_miles)
            .set("ml_partition", wrapper.value.ml_partition)
            .set("distance_from_center", wrapper.value.distance_from_center)
            .set("pickup_latitude", wrapper.value.pickup_latitude)
            .set("pickup_latitude", wrapper.value.pickup_latitude)
            .set("pickup_lat_centered", wrapper.value.pickup_lat_centered)
            .set("pickup_long_centered", wrapper.value.pickup_long_centered)
            .set("pickup_lat_norm", wrapper.value.pickup_lat_norm)
            .set("pickup_long_norm", wrapper.value.pickup_long_norm)
            .set("pickup_lat_std", wrapper.value.pickup_lat_std)
            .set("pickup_long_std", wrapper.value.pickup_long_std)

        wrapper.value.daysOfWeekEncoded?.toSortedMap()?.forEach {
            record.set(it.key, it.value)
        }

        wrapper.value.monthsEncoded?.toSortedMap()?.forEach {
            record.set(it.key, it.value)
        }

        return record.build() as GenericRecord
    }
}