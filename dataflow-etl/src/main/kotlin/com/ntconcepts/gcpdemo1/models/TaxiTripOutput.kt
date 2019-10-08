package com.ntconcepts.gcpdemo1.models

import java.io.Serializable

data class TaxiTripOutput(
    var cash: Int?,
    var year: Int?,
    var start_time: String?,
    var trip_miles: Double?,
    var company: String?,
    var ml_partition: String?,
    var pickup_latitude: Double?,
    var pickup_longitude: Double?,
    var pickup_lat_norm: Double?,
    var pickup_long_norm: Double?,
    var pickup_lat_std: Double?,
    var pickup_long_std: Double?,
    var daysOfWeekEncoded: HashMap<String, Int>?,
    var monthsEncoded: HashMap<String, Int>?,
    var companiesEncoded: HashMap<String, Int>?
) : Serializable {

    constructor() : this(
        0,
        0,
        "",
        0.0,
        "",
        "",
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        HashMap<String, Int>(),
        HashMap<String, Int>(),
        HashMap<String, Int>()
    )
}