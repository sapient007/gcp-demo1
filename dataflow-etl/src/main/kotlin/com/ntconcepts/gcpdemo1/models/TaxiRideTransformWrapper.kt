package com.ntconcepts.gcpdemo1.models

import com.google.api.services.bigquery.model.TableRow
import org.apache.beam.sdk.coders.DefaultCoder
import org.apache.beam.sdk.coders.SerializableCoder
import java.io.Serializable

@DefaultCoder(SerializableCoder::class)
data class TaxiRideTransformWrapper(val ride: TaxiRideL1, var row: TableRow) : Serializable