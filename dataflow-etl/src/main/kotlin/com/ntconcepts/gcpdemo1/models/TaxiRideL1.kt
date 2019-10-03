package com.ntconcepts.gcpdemo1.models

import org.apache.beam.sdk.coders.DefaultCoder
import org.apache.beam.sdk.coders.SerializableCoder
import java.io.Serializable

@DefaultCoder(SerializableCoder::class)
data class TaxiRideL1(
    val unique_key: String,
    val taxi_id: String,
    val trip_start_timestamp: Long?,
    val trip_end_timestamp: Long?,
    val trip_seconds: Long?,
    val trip_miles: Double?,
    val pickup_census_tract: Long?,
    val dropoff_census_tract: Long?,
    val pickup_community_area: Long?,
    val dropoff_community_area: Long?,
    val fare: Double?,
    val tips: Double?,
    val tolls: Double?,
    val extras: Double?,
    val trip_total: Double?,
    val payment_type: String?,
    val company: String?,
    val pickup_latitude: Double?,
    val pickup_longitude: Double?,
    val pickup_location: String?,
    val dropoff_latitude: Double?,
    val dropoff_longitude: Double?,
    val dropoff_location: String?
) : Serializable
